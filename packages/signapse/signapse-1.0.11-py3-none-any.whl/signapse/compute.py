import cv2, math, torch,multiprocessing,imageio
import mediapipe as mp
from signapse.mp_utils import IMAGE_PROCESSING 

mp_holistic = mp.solutions.holistic
mp_face_mesh = mp.solutions.face_mesh

# Given a MediaPipe tensor, find the shoulder centre
def find_shoulder_centre_MP_small_tensor(MP_results_find):
    left_shoulder = MP_results_find[0]
    right_shoulder = MP_results_find[1]
    MP_x_centre = right_shoulder[0] + (left_shoulder[0] - right_shoulder[0]) / 2
    MP_y_centre = right_shoulder[1] + (left_shoulder[1] - right_shoulder[1]) / 2
    return (MP_x_centre,MP_y_centre)
    
# Given a MediaPipe tensor, find the shoulder length
def find_euc_shoulder_distance_MP_small_tensor(MP_results, res):
    left_shoulder = MP_results[0]
    right_shoulder = MP_results[1]    
    x_ = (left_shoulder[0]*res - right_shoulder[0]*res)**2
    y_ = (left_shoulder[1]*res - right_shoulder[1]*res)**2   
    euc_shoulder = math.sqrt(x_ + y_)
    
    ## Vertical scaling
    head_top_point = MP_results[MP_results[48:,1].argmax()+48] 
    head_bottom_point = MP_results[MP_results[48:,1].argmin()+48]
    x_ = (head_top_point[0]*res - head_bottom_point[0]*res)**2
    y_ = (head_top_point[1]*res - head_bottom_point[1]*res)**2
    euc_head = math.sqrt(x_ + y_)
    return euc_shoulder, euc_head
    
# Calculate the required scale and centre of a MediaPipe tensor
def get_scale_and_centre_small_tensor(MP_results_get,loadSize):
    euc_shoulder, euc_head = find_euc_shoulder_distance_MP_small_tensor(MP_results_get, loadSize)
    # optimum_shoulder should be 260 for Marcel
    #optimum_shoulder = 490#440 # Jay#490 #Marcel #260 #200 #210
    if euc_shoulder > 0 and euc_head > 0:
        x_scale =  1 #  optimum_shoulder / euc_shoulder
        MP_scales = [x_scale, x_scale]

        MP_x_centre, MP_y_centre = find_shoulder_centre_MP_small_tensor(MP_results_get)
        MP_x_centre = MP_x_centre * x_scale
        MP_y_centre = MP_y_centre * x_scale
        MP_centres = [MP_x_centre, MP_y_centre]
    else:
        MP_scales  = [0,0]
        MP_centres = [0,0]    
    return torch.tensor(MP_scales),torch.tensor(MP_centres)
    
def face_mesh_landmarks_to_small_tensor(face_mesh_landmarks):
    FM_tensor = torch.stack([torch.tensor([landmark.x, landmark.y]) for landmark in face_mesh_landmarks.landmark])
    return FM_tensor
    
def results_to_small_tensor(data,face_points):
    # Pose landmarks
    if data.pose_landmarks is not None:
        pose_landmarks = torch.stack([torch.tensor([landmark.x, landmark.y]) for landmark in data.pose_landmarks.landmark])
        pose_results = pose_landmarks[11:17]
        hip_results = pose_landmarks[23:25]
    else:
        pose_results = torch.zeros((6,2))
        hip_results = torch.zeros((2,2))
    # Left hand landmarks
    if data.left_hand_landmarks is not None:
        LH_results = torch.stack([torch.tensor([landmark.x, landmark.y]) for landmark in data.left_hand_landmarks.landmark])
        #LH_results[0] = pose_landmarks[15]
    else:
        LH_results = torch.zeros((21,2))
        
    # Right hand landmarks
    if data.right_hand_landmarks is not None:
        RH_results = torch.stack([torch.tensor([landmark.x, landmark.y]) for landmark in data.right_hand_landmarks.landmark])
        #RH_results[0] = pose_landmarks[16]

    else:
        RH_results = torch.zeros((21, 2))
    # Face landmarks
    if data.face_landmarks is not None:
        face_landmarks = torch.stack([torch.tensor([landmark.x, landmark.y]) for landmark in data.face_landmarks.landmark])
        face_results = face_landmarks[list(face_points.keys())]
    else:
        face_results = torch.zeros((128, 2))

    # Make the hand wrist equal to the pose wrist
    LH_results[0] = pose_results[4]
    RH_results[0] = pose_results[5]
    all_results = torch.cat((pose_results, LH_results, RH_results, face_results,hip_results))

    return all_results
    
def worker(image_queue, result_queue,opt):
    with mp_holistic.Holistic(
    static_image_mode=False,
    model_complexity=2,
    smooth_landmarks =True,
    refine_face_landmarks = True,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.8
    ) as holistic:
        if opt.face_mesh:
            face_mesh_model = mp_face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        while True:
            image = image_queue.get()
            if image is None:
                break
            results = holistic.process(image)
            results = results_to_small_tensor(results,opt.face_points)

            if opt.face_mesh:
                # Face Mesh
                results_facemesh = face_mesh_model.process(image)
                results_facemesh = face_mesh_landmarks_to_small_tensor(results_facemesh.multi_face_landmarks[0])
                results = torch.cat((results,results_facemesh))

            result_queue.put(results)

def start_workers(num_workers,opt):
    pool = multiprocessing.Pool(processes=num_workers)
    m = multiprocessing.Manager()
    image_queue = m.Queue()
    result_queue = m.Queue()
    workers = [
        pool.apply_async(worker, (image_queue, result_queue,opt))
        for _ in range(num_workers)
    ]
    return image_queue, result_queue, workers


def parallel_computing(input_video_path,NUM_WORKERS,img_centre, min_size, opt,total_frame):
    print('Parallel computing is running',f"\n")
    FRAME_BUFFER_SIZE = NUM_WORKERS
    image_queue, result_queue, _ = start_workers(num_workers=NUM_WORKERS,opt=opt)
    num_buffer_frames = 0
    pose_tensor,MP_scales, MP_centres = torch.Tensor(),torch.Tensor(),torch.Tensor()
    reader = imageio.get_reader(input_video_path)
    for i, image in enumerate(reader):
        if i <= total_frame:
            image = IMAGE_PROCESSING().apply_norm(image,img_centre,min_size) #
            image.flags.writeable = False        
            if i == 0:
                for _ in range(NUM_WORKERS):
                    image_queue.put(image)
                    num_buffer_frames += 1
                
            image_queue.put(image)
            if num_buffer_frames < FRAME_BUFFER_SIZE:
                num_buffer_frames += 1
                continue
            else:
                MP_results = result_queue.get()
            if MP_results is not None:
                pose_tensor = torch.cat((pose_tensor, MP_results.unsqueeze(0)), dim=0)
                scales, centres = get_scale_and_centre_small_tensor(MP_results,opt.loadSize)
                MP_scales = torch.cat((MP_scales, scales.unsqueeze(0)), dim=0)
                MP_centres = torch.cat((MP_centres, centres.unsqueeze(0)), dim=0)

    for _ in range(FRAME_BUFFER_SIZE):
        MP_results = result_queue.get()
        pose_tensor = torch.cat((pose_tensor, MP_results.unsqueeze(0)), dim=0)
        scales, centres = get_scale_and_centre_small_tensor(MP_results,opt.loadSize)
        MP_scales = torch.cat((MP_scales, scales.unsqueeze(0)), dim=0)
        MP_centres = torch.cat((MP_centres, centres.unsqueeze(0)), dim=0)

    reader.close()
    return pose_tensor[NUM_WORKERS:],MP_scales[NUM_WORKERS:], MP_centres[NUM_WORKERS:]


## serial_computing
def single_worker(image,opt):
    with mp_holistic.Holistic(
    static_image_mode=False,
    model_complexity=2,
    smooth_landmarks =True,
    refine_face_landmarks = True,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.8
    ) as holistic:
        if opt.face_mesh:
            face_mesh_model = mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.8,
                min_tracking_confidence=0.8
            )
        results = holistic.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        results = results_to_small_tensor(results,opt.face_points)

        if opt.face_mesh:
            # Face Mesh
            results_facemesh = face_mesh_model.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            results_facemesh = face_mesh_landmarks_to_small_tensor(results_facemesh.multi_face_landmarks[0])
            results = torch.cat((results,results_facemesh))
    return results
            
def serial_computing(input_video_path, img_centre, min_size, opt, total_frame):
    print('Serial computing is running',f"\n")
    pose_tensor,MP_scales, MP_centres = torch.Tensor(),torch.Tensor(),torch.Tensor()
    reader = imageio.get_reader(input_video_path)
    for i, image in enumerate(reader):
        if i <= total_frame:
            image = IMAGE_PROCESSING().apply_norm(image,img_centre,min_size)
            image.flags.writeable = False
            
            if image is not None:
                MP_results = single_worker(image,opt)
                
            if MP_results is not None:
                pose_tensor = torch.cat((pose_tensor, MP_results.unsqueeze(0)), dim=0)
                scales, centres = get_scale_and_centre_small_tensor(MP_results,opt.loadSize)
                MP_scales = torch.cat((MP_scales, scales.unsqueeze(0)), dim=0)
                MP_centres = torch.cat((MP_centres, centres.unsqueeze(0)), dim=0)
                
    reader.close()
    return pose_tensor,MP_scales, MP_centres
