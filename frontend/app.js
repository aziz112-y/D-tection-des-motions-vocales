const recordBtn = document.getElementById("recordBtn");
const result = document.getElementById("result");

let mediaRecorder;
let isRecording = false; // To track the recording state

recordBtn.addEventListener("click", () => {
  if (!isRecording) {
    // Start recording
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();
        isRecording = true;

        recordBtn.textContent = "Recording... Click to stop";
        const audioChunks = [];

        mediaRecorder.ondataavailable = event => {
          audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
          const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
          const formData = new FormData();
          formData.append('file', audioBlob);

          // Send the audio file to the backend for analysis
          fetch('http://localhost:5000/analyze', { 
            method: 'POST', 
            body: formData,
            headers: {
              'Accept': 'application/json' // Optional: To specify you expect a JSON response
            },
            credentials: 'include'  // Add this line only if you need cookies/session support
          })
          .then(response => response.json())
          .then(data => {
            result.textContent = `Emotion: ${data.emotion} (Confidence: ${data.confidence})`;
            recordBtn.textContent = "Start Recording";
            isRecording = false; // Allow next recording
          })
          .catch(error => {
            console.error("Error analyzing audio:", error);
            result.textContent = "Error analyzing audio.";
            recordBtn.textContent = "Start Recording";
            isRecording = false; // Allow next recording
          });
        };

        // Stop recording when button is clicked again
        recordBtn.textContent = "Click to Stop Recording";
        recordBtn.removeEventListener("click", startRecording);
        recordBtn.addEventListener("click", stopRecording);
      })
      .catch(error => {
        console.error("Microphone access denied or error occurred:", error);
        result.textContent = "Please allow microphone access to record.";
      });
  } else {
    console.warn("Recording is already in progress.");
  }
});

// Function to stop recording
function stopRecording() {
  if (mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    recordBtn.textContent = "Processing...";
  }
}

// Function to start recording
function startRecording() {
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.start();
      isRecording = true;
      recordBtn.textContent = "Recording... Click to stop";
    })
    .catch(error => {
      console.error("Microphone access denied or error occurred:", error);
      result.textContent = "Please allow microphone access to record.";
    });
}
