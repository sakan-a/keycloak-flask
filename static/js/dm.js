const socket = io();
const recipient = window.recipient;
const currentUser = window.currentUser;

socket.emit('join', { recipient });

const form = document.getElementById('chat-form');
const input = document.getElementById('message-input');
const chatBox = document.getElementById('chat-box');

form.addEventListener('submit', function (e) {
    e.preventDefault();
    const message = input.value.trim();
    if (message) {
        socket.emit('send_message', {
            recipient: recipient,
            message: message
        });
        input.value = '';
    }
});

socket.on('receive_message', function (data) {
    const p = document.createElement('p');
    p.innerHTML = `<strong>${data.sender}:</strong> ${data.message}`;
    chatBox.appendChild(p);
});