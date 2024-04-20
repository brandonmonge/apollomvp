const messageList = document.getElementById("messageList");
const userInput = document.getElementById("userInput");
const sendButton = document.getElementById("sendButton");

sendButton.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", function (event) {
  if (event.key === "Enter") {
    sendMessage();
  }
});

function sendMessage() {
  const message = userInput.value.trim();
  if (message !== "") {
    displayMessage("user", message);
    userInput.value = "";

    fetch("http://127.0.0.1:5000/api/generate_response", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: message }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.response) {
          displayMessage("bot", data.response, data.audio_data);
          console.log("Backend response:", data.response);
        } else {
          console.error("Invalid response from backend:", data);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }
}

function displayMessage(sender, message, audioData) {
  const messageElement = document.createElement("div");
  messageElement.classList.add("message");
  messageElement.classList.add(
    sender === "user" ? "user-message" : "bot-message"
  );
  messageElement.textContent = message;
  messageList.appendChild(messageElement);
  messageList.scrollTop = messageList.scrollHeight;

  if (sender === "bot" && audioData) {
    const audioBlob = base64ToBlob(audioData, "audio/mp3");
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    audio.play();
  }
}

function base64ToBlob(base64Data, contentType) {
  const byteCharacters = atob(base64Data);
  const byteNumbers = new Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);
  return new Blob([byteArray], { type: contentType });
}
