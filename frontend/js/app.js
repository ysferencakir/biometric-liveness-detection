document.getElementById('start-btn').addEventListener('click', async () => {
  const video = document.getElementById('video');
  const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
  video.srcObject = stream;
  document.getElementById('status-box').textContent = 'Kamera ve mikrofon erişimi alındı.';
});
