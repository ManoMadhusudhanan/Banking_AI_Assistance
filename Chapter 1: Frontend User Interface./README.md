# Chapter 1: Frontend User Interface
Welcome to the exciting world of our Banking AI Assistant project! In this first chapter, we're going to explore the very first part of our system that you, as a user, will see and interact with: the Frontend User Interface.

## What is the Frontend User Interface?
Imagine you're chatting with a friend on a messaging app. You type your message, send it, and then you see their reply pop up. That whole experience – the chat window, the text box, the send button, and how messages are shown – is what we call a "Frontend User Interface" (often shortened to "Frontend" or "UI").

For our Banking AI Assistant, the Frontend User Interface is like the friendly face of our smart banking system. It's the visual chat window where you can type your questions about your bank account or even upload pictures, and then see the AI's helpful responses.

## Our Goal for This Chapter
By the end of this chapter, you'll understand how a user asks the AI assistant a simple question like: "What is my account balance?" and then sees the AI's reply directly in the chat window.

## Key Parts of Our Frontend
Our Banking AI Assistant's Frontend has several important parts that work together to create a smooth experience:

- **The Chat Window (`chat-body`):** This is the main area where all the conversation happens. You'll see your questions appear, and then the AI's answers pop up.
  
- **The User Input Box (`userInput`):** This is where you type your questions or instructions for the AI. It's like the message box in any chat application.
- **The Send Button (`sendBtn`):** Once you've typed your message, you click this button to send your question to the AI.
- **The Image Upload Button (`uploadBtn`):** Sometimes it's easier to show than tell! This button lets you upload an image (e.g., a screenshot of a transaction) for the AI to look at.
- **The History Panel (`history-panel`):** On the side, you'll see a record of your recent conversations, making it easy to revisit past questions.

## How You Use the Frontend (Solving Our Use Case)
Let's walk through our example: asking "What is my account balance?"

### Step 1: Type Your Question

You'd first click on the text area at the bottom of the chat window and type your question.
```
<!-- From templates/index.html -->
<div class="chat-input-box">
  <!-- ... other elements ... -->
  <textarea
    id="userInput"
    placeholder="Type your question or upload an image..."
  ></textarea>
  <!-- ... other elements ... -->
</div>
```
This textarea with the id="userInput" is where you enter your text.

### Step 2: Send Your Question

After typing, you'd click the "Send" button next to the input box.
```
<!-- From templates/index.html -->
<button id="sendBtn">
  <span>Send</span>
  <i class="fa-solid fa-paper-plane"></i>
</button>
```
When you click this sendBtn, a special function in our JavaScript code named sendMessage() springs into action!

**Here's a simplified look at what happens visually after you send:**

- Your message ("What is my account balance?") immediately appears in the chat window, aligned to the right, showing that you sent it.
- A "Typing…" message appears from the AI, aligned to the left, indicating that the AI is thinking.

### Step 3: See the AI's Reply

After a short moment, the "Typing…" message will be replaced by the AI's actual answer, for example: "Your current account balance is $1,250.75." This message will also be aligned to the left, showing it came from the AI.

```
<!-- A simplified example of how messages are added to the chat body -->
<div id="chatBody" class="chat-body">
  <!-- This is where the messages appear -->
  <div class="msg-row user">
    <div class="msg-bubble user">What is my account balance?</div>
  </div>
  <div class="msg-row bot">
    <div class="msg-bubble bot">Your current account balance is $1,250.75.</div>
  </div>
</div>
```

This chatBody div is the container for all the chat messages. Each message (msg-row) is a separate entry, and msg-bubble holds the actual text.

## What Happens Under the Hood? (Internal Implementation)
Let's peek behind the scenes to see how the Frontend makes all this happen. Think of the Frontend as the "control panel" of a car. When you press the accelerator (type a message and click send), the control panel sends a signal to the engine (the backend AI). The engine then does its work and sends information back to the control panel (the AI's reply), which then displays it to you.

Here's a simple step-by-step breakdown:

<img width="1154" height="592" alt="image" src="https://github.com/user-attachments/assets/65313e33-6001-410b-899d-6bea13bf1d6b" />

- **User Input:** When you type your question and click "Send," the JavaScript code in index.html captures your text from the userInput box.
- **Displaying Your Message:** The Frontend immediately creates a new HTML element to show your question in the chat window, so you know it was sent.
- **Sending to the Backend:** The Frontend then bundles your question (and any uploaded image) and sends it over the internet to the brain of our AI system, which is located in the API Gateway & Orchestration. This "sending" is done using something called an API call.
- **Receiving AI's Reply:** The Frontend waits for a response from the API Gateway & Orchestration.
- **Displaying AI's Reply:** Once the reply arrives, the Frontend updates the chat window. It might first show a "Typing…" message, then replace it with the AI's full answer.
- 
Let's look at the relevant code in `templates/index.html:`

### Adding Messages to the Chat

The addMessage function is responsible for creating those chat bubbles you see.
```
// From templates/index.html
function addMessage(text, sender = "bot") {
  const row = document.createElement("div"); // Create a new container for the message
  row.className = "msg-row " + sender; // Style it as 'user' or 'bot'

  const bubble = document.createElement("div"); // Create the actual message bubble
  bubble.className = "msg-bubble " + sender;
  bubble.innerText = text; // Put the message text inside

  row.appendChild(bubble); // Add the bubble to its container
  chatBody.appendChild(row); // Add the container to the main chat area
  chatBody.scrollTop = chatBody.scrollHeight; // Scroll to the bottom
  return bubble;
}
```
This code snippet shows how new message bubbles are dynamically created and added to the `chatBody` element, making the conversation visible.

### Sending Your Message and Handling the Response

The `sendMessage` function is the heart of sending your input and receiving the AI's reply.
```
// From templates/index.html
async function sendMessage() {
  const text = userInput.value.trim(); // Get text from the input box
  if (!text && !pendingImage) return; // Don't send empty messages

  if (text) {
    addMessage(text, "user"); // Show user's message immediately
    // addHistoryItem(text); // Also add to history (simplified for brevity)
  }
  userInput.value = ""; // Clear the input box

  const loadingBubble = addMessage("Typing…", "bot"); // Show "Typing..." from AI
  sendBtn.disabled = true; // Disable send button during processing

  // Prepare data to send (including a unique session_id and message/image)
  const formData = new FormData();
  formData.append("session_id", getSessionId());
  formData.append("message", text);
  if (pendingImage) { /* ... append image ... */ }

  try {
    const res = await fetch(`${BASE_URL}/chatbot/ask`, { // Send to the backend API
      method: "POST",
      body: formData
    });
    const data = await res.json(); // Get the AI's reply

    // Replace "Typing..." with the actual AI response
    typeWriterEffect(loadingBubble, data?.reply || "⚠️ Could not process your request.");

  } catch (err) { /* ... handle errors ... */ }
  finally {
    sendBtn.disabled = false; // Re-enable send button
    sendBtn.innerHTML = "Send <i class='fa-solid fa-paper-plane'></i>";
  }
}
```
This `sendMessage` function does a lot:

- It grabs what you typed (`userInput.value`).
- It immediately shows your message using `addMessage()`.
- It shows a "Typing…" message from the bot.
- It then uses `fetch()` to send your message to `http://127.0.0.1:8000/chatbot/ask`. This URL points to our [API Gateway & Orchestration] (Chapter 2: API Gateway & Orchestration/README.md)where the AI's "brain" lives.
Once the AI sends back a reply, it updates the `loadingBubble` (the "Typing..." message) with the AI's actual answer usin`g typeWriterEffect()`.

## Image Upload
Our Frontend also supports uploading images!
```
<!-- From templates/index.html -->
<button
    id="uploadBtn"
    title="Upload image"
    style="/* ... styles ... */"
    >
    ➕
</button>
<input
    type="file"
    id="imageInput"
    accept="image/*"
    style="display: none"
/>
```
When you click the "➕" `uploadBtn`, it secretly triggers the hidden `imageInput` to let you select an image file. Once selected, a preview of your image appears in your chat, and when you click "Send", the image is sent along with your text to the backend.

## Conclusion
You've just learned about the **Frontend User Interface**, the part of our Banking AI Assistant that you see and interact with every day! It's responsible for:

- Showing you the conversation in a chat window.
- Allowing you to type questions and upload images.
- Sending your input to the AI's brain.
- Displaying the AI's answers back to you.
  
The Frontend makes the complex AI system accessible and user-friendly. But what happens after you click "Send" and before the AI's reply appears? That's where the next part of our system comes in!

Let's move on to discover how your message travels from the Frontend to the AI's core logic in the next chapter: [API Gateway & Orchestration] (Chapter 2: API Gateway & Orchestration/README.md).
