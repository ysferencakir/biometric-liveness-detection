import cv2

# Load pre-trained Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Open default webcam (camera index 0)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    # Read a frame from camera
    ret, frame = cap.read()
    if not ret:
        print("Error: failed to read frame from webcam.")
        break

    # Convert frame to grayscale for Haar Cascade
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale frame
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    # Draw rectangle(s) according to number of faces
    if len(faces) == 1:
        (x, y, w, h) = faces[0]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    elif len(faces) > 1:
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
    # if no face, just show frame normally

    # Show the result frame
    cv2.imshow("Webcam Face Detection", frame)

    # Exit loop when user presses 'q'
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release camera and close windows
cap.release()
cv2.destroyAllWindows()