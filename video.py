import cv2
import os


def make_video(video_name, image_folder, fps=5):
    log('Creating video...', video_name)

    # Get all images created earlier
    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    # Create video
    log('Creating video with ' + str(len(images)) + ' frames', video_name)
    video = cv2.VideoWriter(video_name + '.avi', 0, fps, (width, height))  # parameters: filename, codec, fps, frameSize

    # Combine all pngs to one video
    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    cv2.destroyAllWindows()
    video.release()

    log('Video created', video_name)

    # Remove images and folder
    for image in images:
        os.remove(os.path.join(image_folder, image))
    os.rmdir(image_folder)
    log('Images removed', video_name)

    return


def log(msg, level='INFO'):
    print('[' + level + '] ' + msg)
    return
