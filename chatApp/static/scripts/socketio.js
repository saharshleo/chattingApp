document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    
    socket.on('connect', () => {
        socket.send('I am connected');
    });

    socket.on('message', (msg) => {
        console.log(`Message received: ${msg}`);
        let msgDisplay = document.createElement('p');
        msgDisplay.innerText = msg
        let listItem = document.createElement('li');
        listItem.appendChild(msgDisplay);
        document.getElementById('messages-list').appendChild(listItem)
    });

    let sendButton = document.querySelector('#send-btn');
    let userInput = document.querySelector('#user-input');

    sendButton.onclick = () => {
        socket.send(userInput.value);
        userInput.value="";
    };

});