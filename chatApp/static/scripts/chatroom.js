document.addEventListener("DOMContentLoaded", () => {

	// Connecting
    var socket = io.connect('http://' + document.domain + ':' + location.port);
	var username = document.querySelector(".username").innerHTML;
	
	// Display received message
    socket.on('message', (msg) => {
        console.log(`Message received: ${msg}`);
        msg = JSON.parse(msg);
        if(msg['room'] !== roomName) {
            console.log("I don't know what to do");
        }
        else {
            let msgDisplay = document.createElement('p');
            msgDisplay.innerText = `${msg["sender"]} (${msg["timestamp"]}): ${msg["content"]}`;
            let listItem = document.createElement('li');
            listItem.appendChild(msgDisplay);
            document.getElementById('messages-list').appendChild(listItem);
        }
    });


	 // Select user input field and send button from DOM
	 let sendButton = document.querySelector('#send-btn');
	 let userInput = document.querySelector('#user-input');

	 // Function to send a message
	 sendMessage = () => {
        if(userInput.value !== '') {
            msg = {
                sender:username,
                content:userInput.value,
            };
            if(roomName) {
                msg['room'] = roomName;
            }
            else {
                console.log("ERROR");
            }
            socket.send(JSON.stringify(msg));
            userInput.value="";
        }
	};
	
	// Listener for send action: Enter key
    userInput.addEventListener("keyup", (e) => {
        if(e.keyCode === 13) {
            if(userInput === document.activeElement) {
                e.preventDefault();
                sendMessage();
            }
        }
    });

    // Listener for send action: Send button clicked
    sendButton.onclick = () => {
        sendMessage();
    };

	// Listener for room-opt clicks
	document.querySelectorAll('.room-opt').forEach(li => {
		
	    li.onclick = () => {
			
	        let newRoom = li.innerHTML;
	        if(newRoom === roomName) {  // User already in that room
	            console.log(`User already in ${roomName}`); // Write alert code later
	        }
	        else {
	            leaveRoom(roomName);
	            joinRoom(newRoom);
	            roomName = newRoom;
	        }
	    }
	});

	// Function for leaving a room
	leaveRoom = (oldRoom) => {
		leave_msg = {
			'sender':username,
			'room':oldRoom
		}
		socket.emit('leave', JSON.stringify(leave_msg));
		document.querySelector('#messages-list').innerHTML = '';
	}

	// Function for joining a roow
	joinRoom = (newRoom) => {
		join_msg = {
			'sender':username,
			'room':newRoom
		}
		socket.emit('join', JSON.stringify(join_msg));
	}

})