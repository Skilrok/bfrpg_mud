/**
 * Game Interface JavaScript
 * Handles the terminal-style game interface with command processing,
 * character data loading, and UI updates.
 */

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const gameOutput = document.querySelector('.game-output');
    const commandInput = document.getElementById('command-input');
    const usernameDisplay = document.getElementById('username');
    const logoutBtn = document.getElementById('logout-btn');
    const charName = document.getElementById('char-name');
    const charClass = document.getElementById('char-class');
    const charLevel = document.getElementById('char-level');
    const charStats = document.querySelector('.stats-list');
    const equipment = document.querySelector('.equipment-list');
    const journalContent = document.querySelector('.journal-content');

    // Authentication state
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username');
    const characterId = localStorage.getItem('characterId');

    // Redirect to login if not authenticated
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    // Set username display
    usernameDisplay.textContent = username || 'Unknown';

    // Logout function
    logoutBtn.addEventListener('click', function() {
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        localStorage.removeItem('characterId');
        window.location.href = 'login.html';
    });

    // Game state
    let gameHistory = [];
    let historyIndex = -1;
    let wsConnection = null;
    let useWebSocket = true;
    let sessionId = generateSessionId();

    // Initialize game
    function initGame() {
        displayMessage("Welcome to Basic Fantasy RPG MUD!", "system");
        displayMessage("Type 'help' for a list of commands.", "system");

        // Try to establish WebSocket connection
        if (useWebSocket) {
            connectWebSocket();
        }

        // Focus the input field
        commandInput.focus();
    }

    // Generate a unique session ID
    function generateSessionId() {
        return 'session_' + Math.random().toString(36).substring(2, 15) +
               Math.random().toString(36).substring(2, 15);
    }

    // Connect to WebSocket for commands
    function connectWebSocket() {
        // Check if browser supports WebSocket
        if (!window.WebSocket) {
            useWebSocket = false;
            displayMessage("Your browser doesn't support WebSockets. Falling back to HTTP.", "system");
            return;
        }

        // Create WebSocket connection
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/commands`;

        try {
            wsConnection = new WebSocket(wsUrl);

            // Connection opened
            wsConnection.onopen = function() {
                // Send authentication data
                wsConnection.send(JSON.stringify({
                    token: token,
                    character_id: characterId,
                    session_id: sessionId
                }));
                displayMessage("WebSocket connected.", "system");
            };

            // Listen for messages
            wsConnection.onmessage = function(event) {
                const data = JSON.parse(event.data);

                if (data.message) {
                    if (!data.success) {
                        displayMessage(data.message, "error");
                    } else {
                        displayMessage(data.message);
                    }
                }

                // Update character info if provided
                if (data.data && data.data.character) {
                    updateCharacterInfo(data.data.character);
                }

                // Update inventory if provided
                if (data.data && data.data.inventory) {
                    updateInventory(data.data.inventory);
                }

                // Update journal if provided
                if (data.data && data.data.journal) {
                    addJournalEntry(data.data.journal);
                }
            };

            // Connection closed
            wsConnection.onclose = function(event) {
                if (event.wasClean) {
                    displayMessage(`WebSocket connection closed. Code=${event.code} reason=${event.reason}`, "system");
                } else {
                    // Connection died
                    displayMessage("WebSocket connection lost. Falling back to HTTP.", "system");
                }

                // Fall back to HTTP for future commands
                useWebSocket = false;
                wsConnection = null;
            };

            // Error handler
            wsConnection.onerror = function(error) {
                displayMessage("WebSocket error. Falling back to HTTP.", "error");
                useWebSocket = false;
            };

        } catch (e) {
            displayMessage("Failed to connect to WebSocket. Using HTTP instead.", "error");
            useWebSocket = false;
        }
    }

    // Display a message in the game output
    function displayMessage(message, type = "normal") {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');

        if (type === "system") {
            messageElement.classList.add('system-message');
            messageElement.innerHTML = `<span class="system-prefix">[SYSTEM]:</span> ${message}`;
        } else if (type === "error") {
            messageElement.classList.add('error-message');
            messageElement.innerHTML = `<span class="error-prefix">[ERROR]:</span> ${message}`;
        } else if (type === "command") {
            messageElement.classList.add('command-message');
            messageElement.innerHTML = `<span class="command-prefix">></span> ${message}`;
        } else {
            messageElement.textContent = message;
        }

        gameOutput.appendChild(messageElement);
        gameOutput.scrollTop = gameOutput.scrollHeight; // Auto-scroll to bottom
    }

    // Send command to server
    async function sendCommand(command) {
        displayMessage(command, "command");

        // Use WebSocket if available, otherwise fall back to HTTP
        if (useWebSocket && wsConnection && wsConnection.readyState === WebSocket.OPEN) {
            // Send via WebSocket
            wsConnection.send(JSON.stringify({
                command: command,
                character_id: characterId,
                session_id: sessionId
            }));
        } else {
            // Fall back to HTTP
            try {
                const response = await fetch('/api/commands/command', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        command: command,
                        character_id: characterId,
                        session_id: sessionId
                    })
                });

                const data = await response.json();

                if (data.message) {
                    if (!data.success) {
                        displayMessage(data.message, "error");
                    } else {
                        displayMessage(data.message);
                    }
                }

                // Update character info if provided
                if (data.data && data.data.character) {
                    updateCharacterInfo(data.data.character);
                }

                // Update inventory if provided
                if (data.data && data.data.inventory) {
                    updateInventory(data.data.inventory);
                }

                // Update journal if provided
                if (data.data && data.data.journal) {
                    addJournalEntry(data.data.journal);
                }

            } catch (error) {
                console.error('Error:', error);
                displayMessage('Failed to send command. Server may be down.', "error");

                // Try to reconnect WebSocket on next command
                if (useWebSocket) {
                    connectWebSocket();
                }
            }
        }
    }

    // Update character information
    function updateCharacterInfo(character) {
        if (character.name) charName.textContent = character.name;
        if (character.character_class) charClass.textContent = `Class: ${character.character_class}`;
        if (character.level) charLevel.textContent = `Level: ${character.level}`;

        // Update stats if available
        if (character.strength || character.dexterity) {
            charStats.innerHTML = '';

            // Add ability scores
            if (character.strength) {
                addStatElement('STR', character.strength);
            }
            if (character.intelligence) {
                addStatElement('INT', character.intelligence);
            }
            if (character.wisdom) {
                addStatElement('WIS', character.wisdom);
            }
            if (character.dexterity) {
                addStatElement('DEX', character.dexterity);
            }
            if (character.constitution) {
                addStatElement('CON', character.constitution);
            }
            if (character.charisma) {
                addStatElement('CHA', character.charisma);
            }

            // Add HP if available
            if (character.hit_points) {
                addStatElement('HP', character.hit_points);
            }

            // Add AC if available
            if (character.armor_class) {
                addStatElement('AC', character.armor_class);
            }
        }
    }

    function addStatElement(name, value) {
        const statElement = document.createElement('li');
        statElement.textContent = `${name}: ${value}`;
        charStats.appendChild(statElement);
    }

    // Update inventory display
    function updateInventory(inventoryItems) {
        equipment.innerHTML = '';

        if (inventoryItems.length === 0) {
            const emptyItem = document.createElement('li');
            emptyItem.textContent = 'Empty';
            equipment.appendChild(emptyItem);
            return;
        }

        inventoryItems.forEach(item => {
            const itemElement = document.createElement('li');
            itemElement.textContent = item.name;
            if (item.equipped) {
                itemElement.classList.add('equipped');
                itemElement.textContent += ' (equipped)';
            }
            equipment.appendChild(itemElement);
        });
    }

    // Add entry to journal
    function addJournalEntry(entry) {
        const journalEntry = document.createElement('div');
        journalEntry.classList.add('journal-entry');

        const dateElement = document.createElement('div');
        dateElement.classList.add('entry-date');
        dateElement.textContent = new Date().toLocaleString();

        const textElement = document.createElement('div');
        textElement.classList.add('entry-text');
        textElement.textContent = entry;

        journalEntry.appendChild(dateElement);
        journalEntry.appendChild(textElement);

        journalContent.appendChild(journalEntry);
        journalContent.scrollTop = journalContent.scrollHeight;
    }

    // Handle command input
    commandInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            const command = commandInput.value.trim();

            if (command) {
                // Add to history
                gameHistory.push(command);
                historyIndex = gameHistory.length;

                // Process command
                sendCommand(command);

                // Clear input
                commandInput.value = '';
            }
        } else if (event.key === 'ArrowUp') {
            // Navigate command history (up)
            if (historyIndex > 0) {
                historyIndex--;
                commandInput.value = gameHistory[historyIndex];

                // Move cursor to end of input
                setTimeout(() => {
                    commandInput.selectionStart = commandInput.selectionEnd = commandInput.value.length;
                }, 0);
            }
            event.preventDefault();
        } else if (event.key === 'ArrowDown') {
            // Navigate command history (down)
            if (historyIndex < gameHistory.length - 1) {
                historyIndex++;
                commandInput.value = gameHistory[historyIndex];
            } else if (historyIndex === gameHistory.length - 1) {
                historyIndex = gameHistory.length;
                commandInput.value = '';
            }
            event.preventDefault();
        }
    });

    // Keep focus on input field when clicking elsewhere in terminal
    document.querySelector('.terminal').addEventListener('click', function() {
        commandInput.focus();
    });

    // Load character data if available
    if (characterId) {
        loadCharacterData(characterId);
    } else {
        displayMessage('\nYou need to select or create a character to play.', "system");
        createCharacterPrompt();
    }

    /**
     * Load character data from API
     * @param {string} id - Character ID to load
     */
    async function loadCharacterData(id) {
        try {
            const response = await fetch(`/api/characters/${id}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();

                // Update character panel
                updateCharacterInfo(data);

                // Load inventory and journal
                loadInventory(id);
                loadJournal(id);

                displayMessage(`\nCharacter ${data.name} loaded. Welcome back!`, "system");
            } else {
                if (response.status === 404) {
                    displayMessage('\nCharacter not found. Please create a new character.', "system");
                } else if (response.status === 401) {
                    displayMessage('\nYour session has expired. Please log in again.', "system");
                    setTimeout(() => logoutBtn.click(), 2000);
                } else {
                    displayMessage('\nFailed to load character data. Please try again later.', "system");
                }
                console.error('Failed to load character data:', response.status);
                createCharacterPrompt();
            }
        } catch (error) {
            console.error('Character data error:', error);
            displayMessage('\nFailed to load character data. Please try again later.', "system");
        }
    }

    /**
     * Load inventory data from API
     * @param {string} characterId - Character ID to load inventory for
     */
    async function loadInventory(characterId) {
        try {
            const response = await fetch(`/api/characters/${characterId}/inventory`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();

                // Update equipment list
                equipment.innerHTML = '';

                if (data.length === 0) {
                    equipment.innerHTML = '<li>No equipment</li>';
                } else {
                    data.forEach(item => {
                        const li = document.createElement('li');
                        li.textContent = item.name;
                        if (item.equipped) {
                            li.classList.add('equipped');
                            li.textContent += ' (equipped)';
                        }
                        equipment.appendChild(li);
                    });
                }
            } else {
                equipment.innerHTML = '<li>Failed to load equipment</li>';
                console.error('Failed to load inventory:', response.status);
            }
        } catch (error) {
            console.error('Inventory error:', error);
            equipment.innerHTML = '<li>Error loading equipment</li>';
        }
    }

    /**
     * Load journal entries from API
     * @param {string} characterId - Character ID to load journal for
     */
    async function loadJournal(characterId) {
        try {
            const response = await fetch(`/api/characters/${characterId}/journal`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data && data.entries && data.entries.length > 0) {
                    journalContent.innerHTML = data.entries.map(entry =>
                        `<div class="journal-entry">
                            <div class="entry-date">${new Date(entry.timestamp).toLocaleDateString()}</div>
                            <div class="entry-text">${entry.text}</div>
                         </div>`
                    ).join('\n');
                } else {
                    journalContent.textContent = 'No journal entries yet.';
                }
            } else {
                journalContent.textContent = 'Failed to load journal entries.';
                console.error('Failed to load journal:', response.status);
            }
        } catch (error) {
            console.error('Journal error:', error);
            journalContent.textContent = 'Error loading journal entries.';
        }
    }

    /**
     * Display character creation prompt
     */
    function createCharacterPrompt() {
        equipment.innerHTML = '<li>No equipment</li>';
        charName.textContent = 'No Character Selected';
        charClass.textContent = 'Class: -';
        charLevel.textContent = 'Level: -';

        displayMessage('\nYou need to create a character to play.');
        displayMessage("Type 'create character <name>' to create a new character.");
    }

    // Initialize the game
    initGame();
});
