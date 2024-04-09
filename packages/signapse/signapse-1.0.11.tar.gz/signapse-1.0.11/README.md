# Signapse synthetic signer
![Signapse](https://static.wixstatic.com/media/45e73d_8ab2ecfdee064f20860fe2a1e3f8ddb2~mv2.png/v1/fill/w_132,h_35,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/Blank%202000%20x%202000%20-%202022-04-03T185113_234.png)

Tested using python=3.10.9

### Example command 

```python inference.py "{\"GPU\":\"cpu\",\"input_video_path\":\"path/to/video.mp4\",\"input_type\":\"video\",\"start\":0,\"stop\":-1,\"num_workers\":1,\"GAN_folder\":\"GAN\",\"signer\":\"Barbara\",\"stereo\":\"False\",\"pro\":\"True\",\"detailed_video\":\"False\",\"organisation_id\":\"0\",\"sign_request_id\":\"0\",\"sign_result_queue_url\":\"0\",\"synthetic_sign_results_bucket\":\"0\"}" ```


## GAN_Checkpoint files

GAN input files need to be downloaded to the respective folders. The GAN files are saved on.

To choose the output signer appearance, pass the respective `--signer XX` argument.

### Barbara

```--signer Barbara```

Download the  folder and store as *./Barbara*. 


### Safyan

```--signer Safyan```

Download the  folder and store as *./Safyan*.

### Mia

```--signer Mia```

Download the folder and store as *./Mia*.

## Face and Body Separate GANs

### To run without Face and Body (--GAN_folder GAN)
 
Pass the respective `--GAN_folder GAN` argument.

```--GAN_folder GAN```

### To run with Face and Body (--GAN_folder GAN_FaB)

Pass the respective `--GAN_folder GAN_FaB` argument.

```--GAN_folder GAN_FaB```

## Face Mesh

### To run with FaceMesh and FaceLandmarks (--GAN_folder GAN_FM)

```--GAN_folder GAN_FM```

### To run with FaceMesh and no FaceLandmarks (--GAN_folder GAN_FM_NoFL)

```--GAN_folder GAN_FM_NoFL```
