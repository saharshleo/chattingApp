document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var username = document.querySelector(".username").innerHTML;
    socket.on('connect', () => {
        socket.send(`${username}~ is connected`);
    });

    socket.on('message', (msg) => {
        console.log(`Message received: ${msg}`);
        msg = JSON.parse(msg);
        let msgDisplay = document.createElement('p');
        msgDisplay.innerText = `${msg["sender"]} (${msg["timestamp"]}): ${msg["content"]}`;
        let listItem = document.createElement('li');
        listItem.appendChild(msgDisplay);
        document.getElementById('messages-list').appendChild(listItem);
    });

    let sendButton = document.querySelector('#send-btn');
    let userInput = document.querySelector('#user-input');

    sendMessage = () => {
        if(userInput.value !== '') {
            msg = {
                sender:username,
                content:userInput.value,
                room:"GLOBAL"
            };

            socket.send(JSON.stringify(msg));
            userInput.value="";
        }
    };

    userInput.addEventListener("keyup", (e) => {
        if(e.keyCode === 13) {
            if(userInput === document.activeElement) {
                e.preventDefault();
                sendMessage();
            };
        };
    });


    sendButton.onclick = () => {
        sendMessage();
    };
});