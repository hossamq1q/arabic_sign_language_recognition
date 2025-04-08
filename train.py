from ultralytics import YOLO

def main():
    model = YOLO('yolov8s.pt') 
    model.train(data='sign.yaml', epochs=50, imgsz=640)

if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    main()

