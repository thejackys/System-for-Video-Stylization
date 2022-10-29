# A system for video stylzing

# Team 12
- B06607057 
- R10944012 
- R10944014 

# Test Platform
- Ubuntu 18.04
- Nvidia RTX 3090, Driver Version 510.73.08, cuda 11.6
- Docker Engine 20.10.14
- Docker Compose 1.29.2

# Steps to use this system
1. Install `docker` and `docker-compose`
2. Install Nvidia Drivers and Setup Cuda Environment
> Note: if no cuda available, or not supported, please comment out the following line in the `docker-compose.yml`
<br>
`runtime: nvidia`
3. cd to `code` directory and extract backend.zip
```
bash
cd code
unzip backend.zip
```
> Note: Source code for frontend is available at `frontend.zip`, but the built version is included in backend.
4. Put the Input Video in the `backend/static/videos` folder and Rename the Video to `video.mp4`
>Note: We assume the video resolution is smaller or equals to 1280x720, and have fps 30. In addition, the ebsynth algorithm is pretty slow, a 4 seconds video can take about 30 minutes to compute. One can use the following command to change the resolution, fps and cut the video into desired length:
<br>
`ffmpeg -i <input> -ss <start_timestamp> -to <end_timestamp> -vf "fps=30, scale=-1:720" video.mp4`
4. Run `docker-compose up`
> Note: The docker-compose will build the docker image and start the backend server.
5. The frontend will be at `localhost:12113`
> Note: The frontend cannot access by multiple client, or it may cause errors.
6. The styled video will be at `backend/static/videos/video_styled.mp4`

# Backup link for demo video
[Demo Video](https://youtu.be/jyE-B--R5ac)

# Credits
This System is based on the following libraries and pretrained model:
## Style Transfer Models for Image
- [Fast Style Transfer in TensorFlow](https://github.com/lengstrom/fast-style-transfer)
- [Domain Enhanced Arbitrary Image Style Transfer via Contrastive Learning (CAST)](https://github.com/zyxElsa/CAST_pytorch)
## Style Transfer algorithm for Video
- [Ebsynth-utils](https://github.com/Krafi2/ebsynth-utils)
- [Ebsynth: A Fast Example-based Image Synthesizer](https://github.com/jamriska/ebsynth)
- [Stylizing Video (Better) by Example](https://github.com/ctrotz/stylizing-video)
## Frontend
- [MUI Core](https://github.com/mui/material-ui)
- [react-slick](https://github.com/akiran/react-slick)
- [React Material File Upload](https://github.com/iamchathu/react-material-file-upload)
- [Video.js - HTML5 Video Player](https://github.com/videojs/video.js)
## Backend
- [Flask](https://github.com/pallets/flask)