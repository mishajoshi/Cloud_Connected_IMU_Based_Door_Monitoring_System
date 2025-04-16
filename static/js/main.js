document.addEventListener('DOMContentLoaded', function() {
    console.log("main.js loaded");
  
    var socket = io();
    var paused = false;      
    var socketActive = true; 
  
    socket.on('connect', function() {
        console.log('Connected to the server via Socket.IO');
        updateConnectionStatus(true);
    });
  
    socket.on('disconnect', function() {
        console.log('Disconnected from the server');
        updateConnectionStatus(false);
    });
  
    socket.on('door_update', function(data) {
        if (!paused) {
            updateDoorStatus(data);
            appendLog(data);
        } else {
            console.log("Updates are paused, skipping UI update.");
        }
    });
  
    function updateDoorStatus(data) {
        var statusElement = document.getElementById("status");
        var timestampElement = document.getElementById("timestamp");
        statusElement.innerText = data.door_state;
        timestampElement.innerText = data.timestamp;
    }
  
    function updateConnectionStatus(connected) {
        var connStatusEl = document.getElementById("connection-status");
        if (connStatusEl) {
            connStatusEl.innerText = connected ? "Connected" : "Disconnected";
            connStatusEl.style.color = connected ? "green" : "red";
        }
    }
  
    function appendLog(data) {
        var logElement = document.getElementById("update-log");
        if (logElement) {
            var row = document.createElement("tr");
      
            var timeCell = document.createElement("td");
            timeCell.innerText = data.timestamp;
            row.appendChild(timeCell);
      
            var statusCell = document.createElement("td");
            statusCell.innerText = data.door_state;
            row.appendChild(statusCell);
      
            logElement.appendChild(row);
        }
    }
  
    // Button event listeners
  
    document.getElementById('btn-pause').addEventListener('click', function() {
        paused = true;
        console.log("UI updates paused");
    });
  
    document.getElementById('btn-resume').addEventListener('click', function() {
        if (!socketActive) {
            socket.connect();
            socketActive = true;
        }
        paused = false;
        console.log("UI updates resumed");
    });
  
    document.getElementById('btn-stop').addEventListener('click', function() {
        socket.disconnect();
        socketActive = false;
        console.log("Socket connection stopped");
    });

    document.getElementById('btn-clear').addEventListener('click', function() {
        var logElement = document.getElementById("update-log");
        if (logElement) {
            logElement.innerHTML = "";
        }
        console.log("Update log cleared");
    });
});
