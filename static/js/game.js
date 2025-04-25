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
    const charClassDetail = document.getElementById('char-class-detail');
    const charLevel = document.getElementById('char-level');
    const charHp = document.getElementById('char-hp');
    const charHpDetail = document.getElementById('char-hp-detail');
    const charRace = document.getElementById('char-race');
    const charStr = document.getElementById('char-str');
    const charInt = document.getElementById('char-int');
    const charWis = document.getElementById('char-wis');
    const charDex = document.getElementById('char-dex');
    const charCon = document.getElementById('char-con');
    const charCha = document.getElementById('char-cha');
    const equipmentList = document.getElementById('equipment-list');
    const journalContent = document.getElementById('journal-content');
    const journalInput = document.getElementById('journal-input');
    const characterSelectionModal = document.getElementById('character-selection-modal');
    const characterListContainer = document.getElementById('character-list');
    const createCharacterBtn = document.getElementById('create-character-btn');
    const partyMembers = document.getElementById('party-members');
    const themeToggleBtn = document.getElementById('theme-toggle');

    // Command input handling
    if (commandInput) {
        commandInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                const command = this.value.trim();
                if (command) {
                    sendCommand(command);
                }
                event.preventDefault();
            }
        });
    }

    // Authentication state
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username');
    let characterId = localStorage.getItem('characterId');

    // Theme toggle functionality
    function initializeTheme() {
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.body.className = savedTheme;
        updateThemeToggleText();
    }

    function toggleTheme() {
        const currentTheme = document.body.className;
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.body.className = newTheme;
        localStorage.setItem('theme', newTheme);
        updateThemeToggleText();
    }

    function updateThemeToggleText() {
        if (themeToggleBtn) {
            const currentTheme = document.body.className;
            themeToggleBtn.textContent = currentTheme === 'dark' ? 'Light Mode' : 'Dark Mode';
        }
    }

    // Initialize theme on page load
    initializeTheme();

    // Add theme toggle event listener
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleTheme);
    }

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

    // Journal entry handling
    if (journalInput) {
        journalInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' && this.value.trim() !== '') {
                const date = new Date();
                const formattedDate = `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;

                addJournalEntry({
                    date: formattedDate,
                    text: this.value.trim()
                });

                // Save journal entry to API (if implemented)
                // saveJournalEntry(characterId, this.value.trim());

                this.value = '';
            }
        });
    }

    // Create new character button is now handled in the inline script in game.html
    /*
    let createCharPending = false;
    createCharacterBtn.addEventListener('click', function() {
        // Prevent multiple clicks
        if (createCharPending) return;

        createCharPending = true;

        // Send a command to begin character creation
        sendCommand('create character New Character');
        hideCharacterSelectionModal();

        // Reset after a delay
        setTimeout(() => {
            createCharPending = false;
        }, 1000);
    });
    */

    // Game state
    let gameHistory = JSON.parse(localStorage.getItem('commandHistory') || '[]');
    let historyIndex = gameHistory.length;
    let wsConnection = null;
    let useWebSocket = true;
    let sessionId = generateSessionId();
    let characters = [];
    let selectedCharacterId = null;
    let partyData = []; // Store party members (character + hirelings)

    // Variables for command debouncing
    let lastCommand = '';
    let lastCommandTime = 0;
    const COMMAND_DEBOUNCE_MS = 500;
    const MAX_HISTORY_SIZE = 50; // Maximum number of commands to store in history

    // Initialize game
    function initGame() {
        // Clear any leftover modal display state
        if (characterSelectionModal) {
            characterSelectionModal.style.display = 'none';
        }

        // Check URL parameters first (they override localStorage)
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('char')) {
            const urlCharId = urlParams.get('char');
            console.log("Found character ID in URL:", urlCharId);
            if (urlCharId) {
                // Set to localStorage and use this
                localStorage.setItem('characterId', urlCharId);
                characterId = urlCharId;
            }
        }

        // Check if we have a character ID
        if (characterId) {
            console.log("Using character ID:", characterId);
            // Show loading message
            displayMessage("Loading character data...", "system");

            // Try to load the character data
            loadCharacterData(characterId)
                .then(success => {
                    if (success) {
                        displayMessage("Welcome to Basic Fantasy RPG MUD!", "system");
                        displayMessage("Type 'help' for a list of commands.", "system");
                        // Load party members (hirelings) if available
                        loadPartyMembers(characterId).catch(err => {
                            console.warn("Failed to load party members:", err);
                            // This isn't critical, so don't show an error to the user
                        });
                    } else {
                        console.error("Failed to load character data for ID:", characterId);
                        // Clear invalid character ID
                        localStorage.removeItem('characterId');
                        characterId = null;

                        // Display friendly error message
                        displayMessage("[ERROR]: Error loading character data. Please try again.", "error");
                        displayMessage("Type 'characters' to open the character selection screen.", "system");
                    }
                })
                .catch(error => {
                    console.error("Error loading character:", error);
                    // Clear invalid character ID
                    localStorage.removeItem('characterId');
                    characterId = null;

                    // Display friendly error message
                    displayMessage("[ERROR]: Error loading character data. Please try again.", "error");
                    displayMessage("Type 'characters' to open the character selection screen.", "system");
                });
        } else {
            // Show welcome message first
            displayMessage("Welcome to Basic Fantasy RPG MUD!", "system");
            displayMessage("You need to select a character to play. Opening character selection...", "system");
            displayMessage("Type 'characters' if you need to reopen the character selection screen.", "system");

            // Use timeout to show character selection after messages
            setTimeout(() => {
                showCharacterSelection();
            }, 500);
        }

        // Try to establish WebSocket connection
        if (useWebSocket) {
            connectWebSocket();
        }

        // Focus the input field
        commandInput.focus();
    }

    // Show character selection modal
    function showCharacterSelection() {
        // Load characters for the user
        loadCharacters()
            .then(chars => {
                characters = chars;
                renderCharacterList();
                characterSelectionModal.classList.add('active');
                characterSelectionModal.style.display = 'block';

                // Add event listener for clicking outside the modal content
                characterSelectionModal.addEventListener('click', function(event) {
                    // If the click is directly on the modal background (not its children)
                    if (event.target === characterSelectionModal) {
                        hideCharacterSelectionModal();
                    }
                });
            })
            .catch(error => {
                console.error("Error loading characters:", error);
                displayMessage("Error loading characters. Please try again later.", "error");
            });
    }

    // Make the showCharacterSelection function available globally
    window.showCharacterSelection = showCharacterSelection;

    // Hide character selection modal
    function hideCharacterSelectionModal() {
        characterSelectionModal.classList.remove('active');
        characterSelectionModal.style.display = 'none';
        console.log("Character selection modal hidden");
    }

    // Load characters for the current user
    async function loadCharacters() {
        try {
            const response = await fetch('/api/characters', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const characters = await response.json();
            return characters;
        } catch (error) {
            console.error("Error loading characters:", error);
            throw error;
        }
    }

    // Render the character list in the selection modal
    function renderCharacterList() {
        characterListContainer.innerHTML = '';

        // Add close button to the modal if it doesn't exist already
        const modalHeader = characterListContainer.parentElement.querySelector('.modal-header');
        if (modalHeader && !modalHeader.querySelector('.close-modal-btn')) {
            const closeButton = document.createElement('button');
            closeButton.classList.add('close-modal-btn');
            closeButton.innerHTML = '&times;';
            closeButton.addEventListener('click', hideCharacterSelectionModal);
            modalHeader.appendChild(closeButton);
        }

        if (characters.length === 0) {
            characterListContainer.innerHTML = `
                <div class="loading-message">
                    No characters found. Click "Create New Character" to get started.
                </div>
            `;
            return;
        }

        characters.forEach(character => {
            const card = document.createElement('div');
            card.classList.add('character-card');
            if (character.id === selectedCharacterId) {
                card.classList.add('selected');
            }

            card.innerHTML = `
                <h3>${character.name}</h3>
                <div class="character-info">
                    <div class="character-info-left">
                        <div class="character-stat">Race: ${character.race}</div>
                        <div class="character-stat">Class: ${character.character_class}</div>
                        <div class="character-stat">Level: ${character.level}</div>
                    </div>
                    <div class="character-info-right">
                        <div class="character-stat">HP: ${character.hit_points}</div>
                        <div class="character-stat">Gold: ${character.gold}</div>
                    </div>
                </div>
                <div class="character-card-actions">
                    <button class="btn select-btn" data-id="${character.id}">Select Character</button>
                    <button class="btn delete-char-btn danger-btn" data-id="${character.id}" data-name="${character.name}">Delete</button>
                </div>
            `;

            characterListContainer.appendChild(card);
        });

        // Attach event listeners to select buttons
        document.querySelectorAll('.select-btn').forEach((btn) => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent the card click from firing
                const charId = btn.getAttribute('data-id');
                if (charId) {
                    selectCharacter(charId);
                }
            });
        });

        // Attach event listeners to delete buttons
        document.querySelectorAll('.delete-char-btn').forEach((btn) => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent the card click from firing
                const charId = btn.getAttribute('data-id');
                const charName = btn.getAttribute('data-name');

                if (charId) {
                    // Show the confirmation modal
                    const confirmDeleteModal = document.getElementById('confirm-delete-modal');
                    const deleteConfirmationMessage = document.getElementById('delete-confirmation-message');
                    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');

                    // Update the confirmation message
                    deleteConfirmationMessage.textContent = `Are you sure you want to delete ${charName}? This action cannot be undone.`;

                    // Set the character ID for the confirm button
                    confirmDeleteBtn.setAttribute('data-id', charId);
                    console.log("Set data-id on confirm button:", charId);

                    // Show the delete confirmation modal
                    confirmDeleteModal.classList.add('active');
                    confirmDeleteModal.style.display = 'block';
                }
            });
        });
    }

    // Select a character and start the game
    function selectCharacter(id) {
        // Ensure id is treated as a string (it might come as a number from API)
        id = String(id);

        // Set character state
        selectedCharacterId = id;
        characterId = id;
        localStorage.setItem('characterId', id);

        console.log("Character selected:", id);

        // Find character info in our list
        const selectedCharacter = characters.find(c => String(c.id) === id);

        // First hide the modal immediately to provide user feedback
        if (characterSelectionModal) {
            hideCharacterSelectionModal();
        }

        // Show a loading message to provide feedback
        displayMessage("Loading character data...", "system");

        // Load the character data
        loadCharacterData(id)
            .then(success => {
                if (success) {
                    if (selectedCharacter) {
                        displayMessage(`Character selected: ${selectedCharacter.name}`, "system");
                    } else {
                        displayMessage("Character selected successfully", "system");
                    }
                    displayMessage("Type 'look' to see your surroundings.", "system");

                    // Load party members
                    loadPartyMembers(id).catch(error => {
                        console.warn("Error loading party members:", error);
                        // Don't display an error to the user, this is not critical
                    });
                } else {
                    displayMessage("Failed to load character data. Please try again.", "error");
                    // Add a helpful command suggestion
                    displayMessage("Type 'characters' to re-open the character selection screen.", "system");
                }
            })
            .catch(error => {
                console.error("Error loading character:", error);
                displayMessage("Error loading character data. Please try again.", "error");
                displayMessage("Type 'characters' to re-open the character selection screen.", "system");
            });
    }

    // Make sure selectCharacter is available globally for the inline script
    window.selectCharacter = selectCharacter;

    // Delete character function
    async function deleteCharacter(id) {
        // Ensure id is treated as a string
        id = String(id);

        console.log("Starting deleteCharacter function with ID:", id);

        try {
            // Show a loading message
            displayMessage("Deleting character...", "system");

            // Log the token (partial) to verify authentication
            if (token) {
                console.log(`Using token: ${token.substring(0, 10)}...`);
            } else {
                console.log("No authentication token found!");
                throw new Error("Authentication token missing");
            }

            // Construct the API URL
            const apiUrl = `/api/characters/${id}`;
            console.log(`Sending DELETE request to ${apiUrl}`);

            // Send DELETE request to the API
            const response = await fetch(apiUrl, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            console.log("Delete response status:", response.status);

            try {
                // Try to parse response as JSON
                const responseData = await response.clone().json();
                console.log("Response data:", responseData);
            } catch (e) {
                // If not JSON, try to get text
                const responseText = await response.clone().text();
                console.log("Response text:", responseText.substring(0, 100));
            }

            // Check if the deletion was successful
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const errorMessage = errorData.detail || `HTTP error! status: ${response.status}`;
                throw new Error(errorMessage);
            }

            // Reload the character list to update the UI
            console.log("Character deleted successfully, reloading character list");
            await loadCharacters()
                .then(chars => {
                    characters = chars;
                    renderCharacterList();

                    // If the deleted character was the currently selected one, clear the selection
                    if (id === characterId) {
                        console.log("Deleted the currently selected character, clearing selection");
                        localStorage.removeItem('characterId');
                        characterId = null;
                        selectedCharacterId = null;

                        // Clear the UI
                        updateCharacterInfo({
                            name: "No Character Selected",
                            race: "",
                            character_class: "",
                            level: "",
                            strength: 0,
                            intelligence: 0,
                            wisdom: 0,
                            dexterity: 0,
                            constitution: 0,
                            charisma: 0,
                            hit_points: 0,
                            armor_class: 0,
                            gold: 0,
                            inventory: [],
                            equipment: []
                        });
                    }

                    displayMessage("Character deleted successfully.", "system");
                });
        } catch (error) {
            console.error("Error deleting character:", error);
            displayMessage(`Error deleting character: ${error.message}`, "error");
        }
    }

    // Make the deleteCharacter function globally available - make sure it's exported correctly
    window.deleteCharacter = deleteCharacter;
    console.log("Exported deleteCharacter function to window:", typeof window.deleteCharacter === 'function');

    // Load party members (character + hirelings)
    async function loadPartyMembers(characterId) {
        try {
            // Load hirelings if the API endpoint exists
            const response = await fetch(`/api/characters/${characterId}/hirelings`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const hirelings = await response.json();
                // Add hirelings to the party data
                partyData = hirelings;
                updatePartyDisplay();
            } else if (response.status !== 404) {
                // Log the error only if it's not a 404 (endpoint might not exist yet)
                console.error("Error loading hirelings:", response.statusText);
            }
        } catch (error) {
            console.error("Error loading party members:", error);
        }
    }

    // Update the party display with character and hirelings
    function updatePartyDisplay() {
        // If partyMembers element doesn't exist, return
        if (!partyMembers) return;

        // Get the character name from the character ID (using the current characterId)
        const characterName = document.getElementById('char-name')?.textContent || 'Character';
        const characterClass = document.getElementById('char-class-level')?.textContent || 'Unknown';
        const characterHP = document.getElementById('char-hp-detail')?.textContent || '?/?';

        // Keep the main character at the top
        // Other party members will be added/updated dynamically
        const mainCharacterHtml = `
            <div class="party-member">
                <div class="party-member-name">${characterName}</div>
                <div class="party-member-info">
                    <div>${characterClass}</div>
                    <div>HP: ${characterHP}</div>
                </div>
            </div>
        `;

        // Start with the main character
        let partyHtml = mainCharacterHtml;

        // Add all hirelings
        if (partyData.length > 0) {
            partyData.forEach(hireling => {
                partyHtml += `
                    <div class="party-member">
                        <div class="party-member-name">${hireling.name}</div>
                        <div class="party-member-info">
                            <div>Class: ${hireling.character_class || 'Unknown'}</div>
                            <div>HP: ${hireling.hit_points || '?'}/${hireling.max_hit_points || '?'}</div>
                        </div>
                    </div>
                `;
            });
        } else {
            // Add placeholder hirelings for demonstration if no hirelings exist
            partyHtml += `
                <div class="party-member">
                    <div class="party-member-name">No hirelings</div>
                    <div class="party-member-info">
                        <div>Hire companions to join your party</div>
                    </div>
                </div>
            `;
        }

        // Update the party display
        partyMembers.innerHTML = partyHtml;
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

        // Make sure we have a fresh token
        const currentToken = localStorage.getItem('token');
        if (!currentToken) {
            displayMessage("Authentication required. Please log in again.", "error");
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
            return;
        }

        // Ensure we have characterId
        if (!characterId) {
            console.warn("No character ID available for WebSocket connection");
            characterId = localStorage.getItem('characterId');
            console.log(`Retrieved character ID from localStorage: ${characterId}`);
        }

        // Create WebSocket connection
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/commands`;

        try {
            // Close existing connection if any
            if (wsConnection && wsConnection.readyState !== WebSocket.CLOSED) {
                wsConnection.close();
            }

            wsConnection = new WebSocket(wsUrl);

            // Connection opened
            wsConnection.onopen = function() {
                // Send authentication data
                const authData = {
                    token: currentToken,
                    character_id: characterId,
                    session_id: sessionId
                };
                console.log("Sending WebSocket auth data:", authData);
                wsConnection.send(JSON.stringify(authData));
                displayMessage("WebSocket connected.", "system");
            };

            // Listen for messages
            // Fixed WebSocket message handling
            wsConnection.onmessage = function(event) {
                try {
                    console.log("WebSocket message received:", event.data);

                    const data = JSON.parse(event.data);

                    // Handle command responses with improved error handling
                    if (data.message) {
                        if (!data.success) {
                            // Handle error messages
                            displayMessage(data.message, "error");

                            // If token is invalid, redirect to login
                            if (data.message && data.message.includes && data.message.includes("Invalid or expired token")) {
                                displayMessage("Session expired. Please log in again.", "error");
                                setTimeout(() => {
                                    localStorage.removeItem('token');
                                    window.location.href = 'login.html';
                                }, 2000);
                            }
                        } else {
                            // Regular success messages
                            displayMessage(data.message, "normal");
                        }
                    } else {
                        // Handle messages without a message property
                        console.warn("WebSocket message missing 'message' property:", data);
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

                    // Log command information if available
                    if (data.command) {
                        console.log("Command processed:", data.command);

                        // Enhanced debug for look command
                        if (data.command.name === "look" || data.command.name === "l") {
                            console.log("LOOK COMMAND RESPONSE:", {
                                success: data.success,
                                message: data.message,
                                data: data.data || {}
                            });

                            // Special handling for look command responses
                            if (data.success && data.data) {
                                // Log room details if available
                                if (data.data.room_id) {
                                    console.log("Room details:", {
                                        id: data.data.room_id,
                                        name: data.data.room_name,
                                        exits: data.data.exits || [],
                                        items: data.data.items || [],
                                        npcs: data.data.npcs || [],
                                        characters: data.data.characters || []
                                    });
                                }
                            }
                        }
                    }
                } catch (e) {
                    console.error("Error processing WebSocket message:", e);
                    displayMessage("Error processing server response. Check console for details.", "error");
                }
            };

            // Connection error
            wsConnection.onerror = function(error) {
                console.error("WebSocket error:", error);
                displayMessage("WebSocket connection error. Trying to reconnect...", "error");
                setTimeout(connectWebSocket, 3000);
            };

            // Connection closed
            wsConnection.onclose = function(event) {
                const reason = event.reason || "Unknown reason";
                displayMessage(`WebSocket connection closed. Code=${event.code} reason=${reason}`, "system");

                // Try to reconnect unless it was a clean close (1000) or authentication issue (4000-4099)
                if (event.code !== 1000 && (event.code < 4000 || event.code > 4099)) {
                    displayMessage("Attempting to reconnect in 3 seconds...", "system");
                    setTimeout(connectWebSocket, 3000);
                } else if (event.code >= 4000 && event.code <= 4099) {
                    // Authentication issue
                    displayMessage("Authentication error. Please log in again.", "error");
                    setTimeout(() => {
                        localStorage.removeItem('token');
                        window.location.href = 'login.html';
                    }, 2000);
                }
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

    // Send a command to the server
    async function sendCommand(command) {
        // Debounce to prevent duplicate rapid command submissions
        const now = Date.now();
        if (command === lastCommand && now - lastCommandTime < COMMAND_DEBOUNCE_MS) {
            console.log("Command debounced:", command);
            return;
        }

        // Update debounce tracking
        lastCommand = command;
        lastCommandTime = now;

        // Add command to history
        gameHistory.push(command);
        historyIndex = gameHistory.length;

        // Special client-side commands
        const commandLower = command.trim().toLowerCase();

        if (commandLower === "characters") {
            displayMessage("Opening character selection...", "system");
            showCharacterSelection();
            commandInput.value = '';
            return;
        }

        if (commandLower.startsWith("select ")) {
            const characterName = command.trim().substring(7);
            if (characterName) {
                selectCharacterByName(characterName);
                commandInput.value = '';
                return;
            }
        }

        // Display the command
        displayMessage(command, "command");

        // If using WebSockets and connected, send via WS
        if (useWebSocket && wsConnection && wsConnection.readyState === WebSocket.OPEN) {
            // Make sure we have the latest character ID
            const currentCharId = localStorage.getItem('characterId') || characterId;

            // Log for debugging purposes
            console.log(`Sending command via WebSocket. Character ID: ${currentCharId}, Command: ${command}`);

            wsConnection.send(JSON.stringify({
                command: command,
                character_id: currentCharId  // Always include character_id with every command
            }));

            // Clear input after sending
            commandInput.value = '';
            return;
        }

        // Otherwise, fall back to HTTP API
        const currentToken = localStorage.getItem('token');
        if (!currentToken) {
            displayMessage("Authentication required. Please log in again.", "error");
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
            return;
        }

        try {
            // Construct headers with current token
            const headers = {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            };

            // Prepare the body
            const body = {
                command: command,
                character_id: characterId,
                session_id: sessionId
            };

            const response = await fetch('/api/commands', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(body)
            });

            const data = await response.json();

            if (data.message) {
                if (!data.success) {
                    displayMessage(data.message, "error");

                    // Check if we need to show character selection
                    if (data.message.includes("need to select or create a character") ||
                        data.message.includes("No active character")) {
                        showCharacterSelection();
                    }
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

    // Expose sendCommand globally for inline scripts
    window.sendCommand = sendCommand;

    // Update character information
    function updateCharacterInfo(character) {
        if (!character) {
            console.warn("Attempted to update character with null data");
            return;
        }

        try {
            console.log("Updating character info with data:", character);

            // Ensure we're specifically setting the character name in the character sheet
            const characterNameElement = document.getElementById('char-name');
            if (characterNameElement) {
                characterNameElement.textContent = character.name || 'Unknown Character';
                console.log("Updated character sheet name to:", character.name);
            } else {
                console.warn("Character name element not found in character sheet");
            }

            // Also update the character name in the party window
            const partyCharNameElement = document.getElementById('party-char-name');
            if (partyCharNameElement) {
                partyCharNameElement.textContent = character.name || 'Unknown Character';
                console.log("Updated party window name to:", character.name);
            } else {
                console.warn("Character name element not found in party window");
            }

            // Update detailed character sheet
            // Basic character information
            const characterClassLevel = `${character.character_class || 'Unknown'} ${character.level || 1}`;

            const classLevelElement = document.getElementById('char-class-level');
            if (classLevelElement) classLevelElement.textContent = characterClassLevel;

            const raceElement = document.getElementById('char-race');
            if (raceElement) raceElement.textContent = character.race || 'Unknown';

            // Safely update ability scores
            safeUpdateAbilityScore('char-str', character.strength || 10);
            safeUpdateAbilityScore('char-dex', character.dexterity || 10);
            safeUpdateAbilityScore('char-con', character.constitution || 10);
            safeUpdateAbilityScore('char-int', character.intelligence || 10);
            safeUpdateAbilityScore('char-wis', character.wisdom || 10);
            safeUpdateAbilityScore('char-cha', character.charisma || 10);

            // Combat stats - safely update them
            const hpDetailElement = document.getElementById('char-hp-detail');
            if (hpDetailElement) hpDetailElement.textContent = `${character.hit_points || 0}/${character.max_hit_points || character.hit_points || 0}`;

            const armorClassElement = document.getElementById('armor-class');
            if (armorClassElement) armorClassElement.textContent = character.armor_class || 10;

            const attackBonusElement = document.getElementById('attack-bonus');
            if (attackBonusElement) attackBonusElement.textContent = character.attack_bonus || '+1';

            const initiativeModElement = document.getElementById('initiative-mod');
            if (initiativeModElement) initiativeModElement.textContent = calculateModifier(character.dexterity || 10);

            const movementElement = document.getElementById('movement');
            if (movementElement) movementElement.textContent = character.movement || '40\'';

            const experienceElement = document.getElementById('experience');
            if (experienceElement) experienceElement.textContent = `${character.experience || 0}/${getXPForNextLevel(character)}`;

            // Safely update saving throws
            const saveDeathElement = document.getElementById('save-death');
            if (saveDeathElement) saveDeathElement.textContent = character.save_death_ray_poison || 12;

            const saveWandsElement = document.getElementById('save-wands');
            if (saveWandsElement) saveWandsElement.textContent = character.save_magic_wands || 13;

            const saveParalysisElement = document.getElementById('save-paralysis');
            if (saveParalysisElement) saveParalysisElement.textContent = character.save_paralysis_petrify || 14;

            const saveBreathElement = document.getElementById('save-breath');
            if (saveBreathElement) saveBreathElement.textContent = character.save_dragon_breath || 15;

            const saveSpellsElement = document.getElementById('save-spells');
            if (saveSpellsElement) saveSpellsElement.textContent = character.save_spells || 16;

            // Try to update class features
            try {
                updateClassFeatures(character);
            } catch (error) {
                console.error("Error updating class features:", error);
            }

            // No longer trying to update inventory here since we'll use the dedicated loadInventory function
            // which makes a separate API call to get the complete inventory

            // Try to update weapons
            try {
                updateWeaponsList(character.weapons || []);
            } catch (error) {
                console.error("Error updating weapons:", error);
            }

            // Try to update party display
            try {
                updatePartyDisplay();
            } catch (error) {
                console.error("Error updating party display:", error);
            }

        } catch (error) {
            console.error("Error updating character info:", error);
            // Don't let errors here prevent the game from loading
        }
    }

    // Safe version of updateAbilityScore that won't crash if elements are missing
    function safeUpdateAbilityScore(elementId, score) {
        try {
            const element = document.getElementById(elementId);
            if (element) {
                element.textContent = score;
                // Also update the modifier
                const modId = `${elementId}-mod`;
                const modElement = document.getElementById(modId);
                if (modElement) {
                    modElement.textContent = calculateModifier(score);
                }
            }
        } catch (error) {
            console.error(`Error updating ability score ${elementId}:`, error);
        }
    }

    // Helper function to calculate ability modifier
    function calculateModifier(abilityScore) {
        // Ensure we're working with a number
        const score = parseInt(abilityScore) || 10;
        const mod = Math.floor((score - 10) / 2);
        // Return as a formatted string with + or - sign
        return mod >= 0 ? `+${mod}` : `${mod}`;
    }

    // Helper function to get XP needed for next level
    function getXPForNextLevel(character) {
        const level = character.level || 1;
        // Basic XP progression - customize based on your game rules
        const xpTable = [0, 2000, 4000, 8000, 16000, 32000, 64000, 120000, 240000, 360000];
        return xpTable[level] || xpTable[xpTable.length - 1];
    }

    // Update class features based on character class
    function updateClassFeatures(character) {
        const featuresElement = document.getElementById('class-features');
        if (!featuresElement) return;

        const charClass = character.character_class || '';
        let featuresHTML = '';

        // Display class-specific features
        switch(charClass.toLowerCase()) {
            case 'cleric':
                featuresHTML = `
                    <div>Turn Undead</div>
                    <div>Spell Casting</div>
                    <div>Spells per day: ${getSpellsPerDay(character)}</div>
                `;
                break;
            case 'fighter':
                featuresHTML = `
                    <div>Combat Expertise</div>
                    <div>Bonus to-hit: ${calculateModifier(character.strength || 10)}</div>
                `;
                break;
            case 'magic-user':
                featuresHTML = `
                    <div>Spell Casting</div>
                    <div>Spells per day: ${getSpellsPerDay(character)}</div>
                    <div>Spells known: ${(character.spells_known || []).join(', ') || 'None'}</div>
                `;
                break;
            case 'thief':
                featuresHTML = createThiefSkillsHTML(character);
                break;
            default:
                featuresHTML = '<div>No special class features</div>';
        }

        featuresElement.innerHTML = featuresHTML;
    }

    // Helper function to get the currently active character
    function getCurrentCharacter() {
        // Check if we're still loading character data
        const loadingMessage = document.querySelector('#message-container .message-system');
        if (loadingMessage && loadingMessage.textContent.includes('Loading character data')) {
            console.log("Character data is still loading, returning null");
            return null;
        }

        // First look for the character in the global state
        if (characterId && characters && characters.length) {
            const character = characters.find(c => String(c.id) === String(characterId));
            if (character) {
                console.log("Found character in global state:", character.name);
                return character;
            }
        }

        // If not found, try to get it from DOM elements
        try {
            const nameElement = document.getElementById('character-name');
            const raceElement = document.getElementById('character-race');
            const classElement = document.getElementById('character-class');
            const levelElement = document.getElementById('character-level');
            const strengthElement = document.getElementById('strength-score');
            const dexterityElement = document.getElementById('dexterity-score');
            const constitutionElement = document.getElementById('constitution-score');
            const intelligenceElement = document.getElementById('intelligence-score');
            const wisdomElement = document.getElementById('wisdom-score');
            const charismaElement = document.getElementById('charisma-score');

            // Check if all elements exist before trying to access their content
            if (!nameElement || !raceElement || !classElement || !levelElement) {
                console.warn("Character UI elements not found, character data may not be loaded yet");
                return null;
            }

            return {
                id: characterId,
                name: nameElement.textContent || "Unknown",
                race: raceElement.textContent || "Unknown",
                character_class: classElement.textContent || "Fighter",
                level: levelElement.textContent || "1",
                abilities: {
                    strength: (strengthElement && strengthElement.textContent) || "10",
                    dexterity: (dexterityElement && dexterityElement.textContent) || "10",
                    constitution: (constitutionElement && constitutionElement.textContent) || "10",
                    intelligence: (intelligenceElement && intelligenceElement.textContent) || "10",
                    wisdom: (wisdomElement && wisdomElement.textContent) || "10",
                    charisma: (charismaElement && charismaElement.textContent) || "10"
                }
            };
        } catch (error) {
            console.warn("Could not construct character from DOM:", error);
            return null;
        }
    }

    // Get spells per day based on class and level
    function getSpellsPerDay(character) {
        const level = character.level || 1;
        const charClass = character.character_class || '';

        // Simple placeholder - you would replace with actual rules
        if (charClass.toLowerCase() === 'magic-user') {
            return level > 1 ? '2/1' : '1';
        } else if (charClass.toLowerCase() === 'cleric') {
            return level > 1 ? '1' : '0';
        }

        return '0';
    }

    // Create HTML for thief skills
    function createThiefSkillsHTML(character) {
        const thiefSkills = character.thief_abilities || {};
        return `
            <div class="thief-skills">
                <div class="skill"><span>Open Locks:</span> <span>${thiefSkills.open_locks || 15}%</span></div>
                <div class="skill"><span>Remove Traps:</span> <span>${thiefSkills.remove_traps || 10}%</span></div>
                <div class="skill"><span>Pick Pockets:</span> <span>${thiefSkills.pick_pockets || 20}%</span></div>
                <div class="skill"><span>Move Silently:</span> <span>${thiefSkills.move_silently || 20}%</span></div>
                <div class="skill"><span>Climb Walls:</span> <span>${thiefSkills.climb_walls || 85}%</span></div>
                <div class="skill"><span>Hide:</span> <span>${thiefSkills.hide || 10}%</span></div>
                <div class="skill"><span>Listen:</span> <span>${thiefSkills.listen || 30}%</span></div>
            </div>
        `;
    }

    // Helper function to calculate a character's attack bonus with a weapon
    function getCharacterAttackBonus(character, weapon) {
        if (!character) return "--";
        if (!weapon || !weapon.name) return "--";

        console.log("Calculating attack bonus for weapon:", weapon.name);

        // Base attack bonus from character class and level
        let baseAttack = 0;
        const level = parseInt(character.level) || 1;

        // Different classes have different attack progression
        const charClass = (character.character_class || character.class || "").toLowerCase();

        if (charClass.includes("fighter") || charClass.includes("dwarf") || charClass.includes("elf")) {
            baseAttack = Math.floor(level);
        } else if (charClass.includes("cleric") || charClass.includes("thief") || charClass.includes("halfling")) {
            baseAttack = Math.floor(level * 0.75);
        } else if (charClass.includes("magic-user")) {
            baseAttack = Math.floor(level * 0.5);
        } else {
            // Default progression
            baseAttack = Math.floor(level * 0.75);
        }

        // Add strength modifier for melee weapons or dexterity for ranged weapons
        let abilityMod = 0;

        // Check if character has abilities
        if (character.abilities) {
            const str = parseInt(character.abilities.strength) || 10;
            const dex = parseInt(character.abilities.dexterity) || 10;

            // Determine if weapon is ranged
            const isRanged = weapon.name.toLowerCase().includes('bow') ||
                              weapon.name.toLowerCase().includes('crossbow') ||
                              weapon.name.toLowerCase().includes('sling');

            if (isRanged) {
                // Use dexterity for ranged weapons
                abilityMod = calculateModifier(dex);
            } else {
                // Use strength for melee weapons
                abilityMod = calculateModifier(str);
            }
        }

        // Calculate total attack bonus
        const totalBonus = baseAttack + abilityMod;

        // Format as +X or -X
        return totalBonus >= 0 ? `+${totalBonus}` : `${totalBonus}`;
    }

    // Helper function to determine standard weapon damage based on weapon name
    function getStandardWeaponDamage(weaponName) {
        if (!weaponName) return "--";

        const name = weaponName.toLowerCase();

        // Basic Fantasy RPG standard weapon damages
        if (name.includes('dagger') || name.includes('dart')) {
            return "1d4";
        } else if (name.includes('hand axe') || name.includes('club') ||
                  name.includes('hammer') || name.includes('mace') ||
                  name.includes('staff') || name.includes('short sword')) {
            return "1d6";
        } else if (name.includes('spear') || name.includes('long sword') ||
                  name.includes('battle axe') || name.includes('flail') ||
                  name.includes('war hammer')) {
            return "1d8";
        } else if (name.includes('two-handed sword') || name.includes('pole arm')) {
            return "1d10";
        } else if (name.includes('shortbow') || name.includes('short bow')) {
            return "1d6";
        } else if (name.includes('longbow') || name.includes('long bow')) {
            return "1d8";
        } else if (name.includes('crossbow')) {
            return "1d6";
        } else if (name.includes('sling')) {
            return "1d4";
        } else {
            // Default damage if we can't identify the weapon
            return "1d6";
        }
    }

    // Update weapons table
    function updateWeaponsList(weapons) {
        console.log("Updating weapons list with:", weapons);
        // Get the weapons container
        const weaponsList = document.getElementById('weapons-list');
        if (!weaponsList) {
            console.error("Weapons list element not found");
            return;
        }

        // Clear current weapons
        weaponsList.innerHTML = '';

        if (!weapons || weapons.length === 0) {
            console.log("No weapons to display");
            const row = weaponsList.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 4;
            cell.textContent = 'No weapons';
            return;
        }

        // Add weapons to the table
        weapons.forEach(weapon => {
            console.log("Processing weapon object:", weapon);

            // Safely extract properties from multiple possible locations
            const properties = (typeof weapon.properties === 'object') ? weapon.properties : {};

            // Extract weapon name
            const name = weapon.name || 'Unknown weapon';

            // Extract attack bonus
            let attackBonus = '+0';

            // First try the attack property directly
            if (weapon.attack !== undefined) {
                attackBonus = weapon.attack;
            } else if (properties.attack !== undefined) {
                attackBonus = properties.attack;
            } else if (weapon.item_data && weapon.item_data.attack !== undefined) {
                attackBonus = weapon.item_data.attack;
            } else {
                // Calculate attack bonus based on character stats if available
                try {
                    const character = getCurrentCharacter();
                    if (character) {
                        attackBonus = getCharacterAttackBonus(character, weapon);
                    }
                } catch (e) {
                    console.warn("Could not calculate attack bonus:", e);
                }
            }

            // Make sure attack bonus has a + or - prefix
            if (typeof attackBonus === 'number') {
                attackBonus = (attackBonus >= 0 ? '+' : '') + attackBonus;
            } else if (typeof attackBonus === 'string' && !attackBonus.startsWith('+') && !attackBonus.startsWith('-')) {
                attackBonus = '+' + attackBonus;
            }

            // Extract damage
            let damage = '1d6';  // Default damage

            if (weapon.damage) {
                damage = weapon.damage;
            } else if (properties.damage) {
                damage = properties.damage;
            } else if (weapon.item_data && weapon.item_data.damage) {
                damage = weapon.item_data.damage;
            } else {
                // Try to determine standard damage based on weapon name
                const standardDamage = getStandardWeaponDamage(weapon.name);
                if (standardDamage) {
                    damage = standardDamage;
                }
            }

            // Generate notes
            let notes = '';

            // Add weapon type if available
            if (weapon.weapon_type || properties.weapon_type) {
                notes = weapon.weapon_type || properties.weapon_type;
            }

            // Add range information if available
            if (weapon.range || properties.range) {
                const range = weapon.range || properties.range;
                if (notes) notes += ', ';
                notes += `Range: ${range}`;
            }

            // Add weight if available
            if (weapon.weight || properties.weight) {
                const weight = weapon.weight || properties.weight;
                if (notes) notes += ', ';
                notes += `Weight: ${weight}`;
            }

            // Add any special properties
            if (weapon.special || properties.special) {
                const special = weapon.special || properties.special;
                if (notes) notes += ', ';
                notes += `Special: ${special}`;
            }

            // Check if weapon is equipped
            const isEquipped = weapon.equipped ||
                (properties.equipped) ||
                (weapon.item_data && weapon.item_data.equipped);

            const row = weaponsList.insertRow();

            // Add weapon name (with equipped indicator if needed)
            const nameCell = row.insertCell();
            nameCell.textContent = isEquipped ? `${name} (equipped)` : name;
            if (isEquipped) {
                nameCell.style.fontWeight = 'bold';
            }

            // Add attack bonus
            const attackCell = row.insertCell();
            attackCell.textContent = attackBonus;

            // Add damage
            const damageCell = row.insertCell();
            damageCell.textContent = damage;

            // Add notes
            const notesCell = row.insertCell();
            notesCell.textContent = notes;
        });
    }

    // Backward compatibility function that calls updateWeaponsList
    function updateWeapons(weapons) {
        console.log("updateWeapons called, forwarding to updateWeaponsList");
        return updateWeaponsList(weapons);
    }

    // Function to load inventory data from API
    async function loadInventory(characterId) {
        console.log(`Loading inventory for character ${characterId}`);
        if (!characterId) {
            console.error("No character ID provided for loadInventory");
            return;
        }

        try {
            const token = localStorage.getItem('token');
            if (!token) {
                console.error("No auth token found for inventory request");
                return;
            }

            // Fetch inventory data using the inventory command API
            const response = await fetch(`/api/commands`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    character_id: characterId,
                    command: "inventory"
                })
            });

            if (!response.ok) {
                throw new Error(`Failed to fetch inventory: ${response.status}`);
            }

            const data = await response.json();
            console.log("Inventory command response:", data);

            // If command was successful and returned inventory data
            if (data.success && data.data && data.data.inventory) {
                // Update the inventory in the UI
                updateInventory(data.data.inventory);
            } else {
                console.warn("Inventory command did not return valid data:", data);
                // Try to parse inventory from the message as fallback
                if (data.success && data.message) {
                    console.log("Attempting to extract inventory from command message");
                    displayMessage(data.message);
                }
            }
        } catch (error) {
            console.error("Error loading inventory:", error);
            displayMessage("Failed to load inventory. Please try again.", "error");
        }
    }

    // Update the inventory list display to show all general items
    function updateInventoryList(inventory) {
        console.log("Updating inventory list with:", inventory);
        const inventoryList = document.getElementById('inventory-list');
        if (!inventoryList) {
            console.error("Inventory list element not found");
            return;
        }

        // Clear current inventory display
        inventoryList.innerHTML = '';

        // If no inventory items, show a message
        if (!inventory || inventory.length === 0) {
            const emptyItem = document.createElement('li');
            emptyItem.textContent = 'No items in inventory';
            inventoryList.appendChild(emptyItem);
            return;
        }

        // Add each item to the inventory list
        inventory.forEach(item => {
            const listItem = document.createElement('li');
            listItem.className = 'inventory-item';

            // Get item name with fallback
            const itemName = item.name || 'Unknown item';

            // Check if item is equipped
            const isEquipped = item.equipped ||
                (item.properties && item.properties.equipped) ||
                (item.item_data && item.item_data.equipped);

            // Create the item name with equipped status if applicable
            let itemText = itemName;
            if (isEquipped) {
                itemText += ' (equipped)';
                listItem.classList.add('equipped');
            }

            // Add quantity if more than 1
            if (item.quantity && item.quantity > 1) {
                itemText = `${itemName} (${item.quantity})`;
            }

            listItem.textContent = itemText;

            // Add tooltip with description if available
            if (item.description) {
                listItem.title = item.description;
            }

            inventoryList.appendChild(listItem);
        });
    }

    // Function to update inventory with the provided data
    function updateInventory(inventory) {
        console.log("Updating inventory with data:", JSON.stringify(inventory, null, 2));

        // Update the general inventory list
        updateInventoryList(inventory);

        // Extract weapons and armor from inventory
        let weapons = [];
        let armorItems = [];

        if (Array.isArray(inventory)) {
            // Check structure of inventory item for logging
            if (inventory.length > 0) {
                console.log("First inventory item structure:", Object.keys(inventory[0]));
            }

            // Filter items into weapons and armor
            inventory.forEach(item => {
                // Debug each inventory item
                console.log("Processing inventory item:", item.name, "type:", item.item_type);

                if (!item.item_type) {
                    console.log("Item missing item_type:", item);
                }

                if (item.item_type === 'weapon') {
                    weapons.push(item);
                } else if (item.item_type === 'armor' || item.item_type === 'shield') {
                    armorItems.push(item);
                } else if (item.type && (item.type.toLowerCase() === 'weapon' ||
                           (item.item_subtype && item.item_subtype.toLowerCase() === 'weapon'))) {
                    // Alternative property naming for weapons
                    weapons.push(item);
                } else if (item.name && (
                    item.name.toLowerCase().includes('sword') ||
                    item.name.toLowerCase().includes('axe') ||
                    item.name.toLowerCase().includes('mace') ||
                    item.name.toLowerCase().includes('dagger') ||
                    item.name.toLowerCase().includes('staff') ||
                    item.name.toLowerCase().includes('club') ||
                    item.name.toLowerCase().includes('hammer') ||
                    item.name.toLowerCase().includes('bow') ||
                    item.name.toLowerCase().includes('crossbow') ||
                    item.name.toLowerCase().includes('sling')
                )) {
                    // If item name suggests a weapon but item_type is missing
                    console.log("Detected likely weapon by name:", item.name);
                    // Clone the item and ensure it has item_type
                    const weaponItem = {...item, item_type: 'weapon'};
                    weapons.push(weaponItem);
                } else if (item.name && (
                    item.name.toLowerCase().includes('armor') ||
                    item.name.toLowerCase().includes('plate') ||
                    item.name.toLowerCase().includes('mail') ||
                    item.name.toLowerCase().includes('leather') ||
                    item.name.toLowerCase().includes('shield') ||
                    item.name.toLowerCase().includes('helm') ||
                    item.name.toLowerCase().includes('robe') ||
                    item.name.toLowerCase().includes('cloak')
                )) {
                    // If item name suggests armor but item_type is missing
                    console.log("Detected likely armor by name:", item.name);
                    const armorItem = {...item, item_type: item.name.toLowerCase().includes('shield') ? 'shield' : 'armor'};
                    armorItems.push(armorItem);
                }
            });

            console.log(`Found ${weapons.length} weapons and ${armorItems.length} armor items`);
        } else {
            console.warn("Inventory is not an array:", inventory);
        }

        // Update weapon list
        try {
            updateWeaponsList(weapons);
        } catch (error) {
            console.error("Error updating weapons list:", error);
        }

        // Update armor list
        try {
            updateArmorList(armorItems);
        } catch (error) {
            console.error("Error updating armor list:", error);
        }

        // Update equipped items
        try {
            updateEquippedItems(inventory);
        } catch (error) {
            console.error("Error updating equipped items:", error);
        }
    }

    // Function to update equipped items
    function updateEquippedItems(inventory) {
        console.log("Updating equipped items with inventory:", inventory);

        // Find equipped items by slot
        const equippedItems = {
            head: null,
            body: null,
            mainHand: null,
            offHand: null
        };

        if (Array.isArray(inventory)) {
            inventory.forEach(item => {
                console.log("Checking item for equipped status:", item.name, "equipped:", item.equipped);

                // Check all possible ways an item might be marked as equipped
                const isEquipped = item.equipped ||
                    (item.properties && item.properties.equipped) ||
                    (item.item_data && item.item_data.equipped);

                if (isEquipped) {
                    console.log("Found equipped item:", item.name);

                    // Determine which slot based on item data
                    const slotName = item.slot ||
                                (item.properties && item.properties.slot);

                    // Map slot names from the API to our UI slots
                    if (slotName) {
                        // If item has an explicit slot property, use a standardized name
                        const mappedSlot = {
                            'head': 'head',
                            'helmet': 'head',
                            'headgear': 'head',
                            'body': 'body',
                            'armor': 'body',
                            'main_hand': 'mainHand',
                            'main hand': 'mainHand',
                            'mainhand': 'mainHand',
                            'primary': 'mainHand',
                            'off_hand': 'offHand',
                            'off hand': 'offHand',
                            'offhand': 'offHand',
                            'secondary': 'offHand',
                            'shield': 'offHand'
                        }[slotName.toLowerCase()] || slotName;

                        if (equippedItems.hasOwnProperty(mappedSlot)) {
                            equippedItems[mappedSlot] = item;
                        }
                    } else if (item.item_type === 'helmet' || item.item_type === 'headgear') {
                        equippedItems.head = item;
                    } else if (item.item_type === 'armor' || item.item_type === 'robe') {
                        equippedItems.body = item;
                    } else if (item.item_type === 'weapon' && (!equippedItems.mainHand || item.primary_weapon)) {
                        equippedItems.mainHand = item;
                    } else if (item.item_type === 'shield') {
                        equippedItems.offHand = item;
                    } else if (item.item_type === 'weapon' && !equippedItems.offHand) {
                        // Only put a second weapon in offhand if nothing else is there
                        equippedItems.offHand = item;
                    }
                }
            });
        }

        console.log("Equipped items by slot:", equippedItems);

        // Update the UI with equipped items
        updateEquippedItemDisplay('Head', equippedItems.head);
        updateEquippedItemDisplay('Body', equippedItems.body);
        updateEquippedItemDisplay('Main Hand', equippedItems.mainHand);
        updateEquippedItemDisplay('Off Hand', equippedItems.offHand);
    }

    // Helper function to update a specific equipped item slot display
    function updateEquippedItemDisplay(slotName, item) {
        // Map slot names to HTML element IDs
        const slotIdMap = {
            'Head': 'slot-head',
            'Body': 'slot-body',
            'Main Hand': 'slot-main-hand',
            'Off Hand': 'slot-off-hand'
        };

        const slotId = slotIdMap[slotName];
        if (!slotId) {
            console.warn(`Unknown slot name: ${slotName}`);
            return;
        }

        const slotElement = document.getElementById(slotId);
        if (!slotElement) {
            console.warn(`Could not find element for slot ID: ${slotId}`);
            return;
        }

        // Update the slot with item info or clear it
        if (item) {
            slotElement.textContent = item.name || 'Unknown item';
            // You can add more info like a tooltip with item.description if needed
        } else {
            slotElement.textContent = '-';
        }
    }

    // Update the armor table
    function updateArmorList(armorItems) {
        console.log("Updating armor list with:", armorItems);
        const armorList = document.getElementById('armor-list');
        if (!armorList) {
            console.error("Armor list element not found");
            return;
        }

        // Clear current armor list
        armorList.innerHTML = '';

        // If no armor, display a message
        if (!armorItems || armorItems.length === 0) {
            const row = armorList.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 4;
            cell.textContent = 'No armor';
            return;
        }

        // Add each armor item to the table
        armorItems.forEach(armor => {
            // Debug log to see armor structure
            console.log("Processing armor object:", JSON.stringify(armor, null, 2));

            const row = armorList.insertRow();

            // Safely get properties from multiple possible locations
            // Use nullish coalescing to handle missing properties gracefully
            const properties = (typeof armor.properties === 'object') ? armor.properties : {};

            // Extract armor info, with fallbacks for different property names
            const name = armor.name || 'Unknown';
            
            // Get AC value - check ac_bonus column first (for shields), then armor_class, then properties
            let ac = 0;
            if (armor.item_type === 'shield') {
                // For shields, prioritize ac_bonus column
                ac = armor.ac_bonus ?? (properties.ac_bonus ?? 0);
            } else {
                // For regular armor
                ac = armor.armor_class ?? (properties.armor_class ?? 0);
            }

            // Determine armor type
            let type = 'Unknown';
            if (armor.item_type === 'shield') {
                type = 'Shield';
            } else if (armor.armor_type) {
                type = armor.armor_type;
            } else if (properties.type) {
                type = properties.type;
            } else if (armor.item_type) {
                type = armor.item_type.charAt(0).toUpperCase() + armor.item_type.slice(1);
            }

            // Generate notes text
            let notes = '';

            // Check if armor is equipped
            const isEquipped = armor.equipped ||
                           (properties.equipped) ||
                           (armor.item_data && armor.item_data.equipped);

            if (isEquipped) {
                notes += 'Equipped';
            }

            // Add weight if available
            if (armor.weight || properties.weight) {
                const weight = armor.weight || properties.weight;
                if (notes) notes += ', ';
                notes += `Weight: ${weight}`;
            }

            // Add any additional properties useful for armor
            if (properties.material) {
                if (notes) notes += ', ';
                notes += `Material: ${properties.material}`;
            }

            if (properties.restrictions || armor.restrictions) {
                const restrictions = properties.restrictions || armor.restrictions;
                if (notes) notes += ', ';
                notes += `Restrictions: ${restrictions}`;
            }

            // Add armor name cell (with equipped indicator)
            const nameCell = row.insertCell();
            nameCell.textContent = isEquipped ? `${name} (equipped)` : name;
            if (isEquipped) {
                nameCell.style.fontWeight = 'bold';
            }

            // Add AC
            const acCell = row.insertCell();
            acCell.textContent = ac;

            // Add armor type
            const typeCell = row.insertCell();
            typeCell.textContent = type;

            // Add notes
            const notesCell = row.insertCell();
            notesCell.textContent = notes;
        });
    }

    // Load character data from API
    async function loadCharacterData(id, retryCount = 0) {
        if (!id) {
            console.error("Invalid character ID:", id);
            return false;
        }

        try {
            console.log(`Attempting to load character data for ID: ${id}`);

            // First, ensure we have the character in our list of characters
            if (!characters || characters.length === 0) {
                try {
                    // If we don't have characters yet, try to load them
                    console.log("No characters loaded yet, fetching list from server");
                    characters = await loadCharacters();
                    console.log("Loaded characters:", characters);
                } catch (error) {
                    console.error("Error loading characters list:", error);
                    // Continue anyway, we'll handle this below
                }
            }

            // Try to find the character in our current list
            const cachedCharacter = characters.find(c => String(c.id) === String(id));
            if (cachedCharacter) {
                console.log(`Found cached character: ${cachedCharacter.name}`);
            } else {
                console.log(`No cached character found for ID: ${id}`);
                // Clear the invalid character ID if it's not in our list
                if (characters && characters.length > 0) {
                    console.warn("Character ID not found in available characters, clearing it");
                    return false;
                }
            }

            // Create a minimal character object to ensure the UI works even if we can't get data
            const minimumCharacterData = {
                id: id,
                name: cachedCharacter ? cachedCharacter.name : `Character ${id}`,
                race: cachedCharacter ? cachedCharacter.race : "Unknown",
                character_class: cachedCharacter ? cachedCharacter.character_class : "Fighter",
                level: cachedCharacter ? cachedCharacter.level : 1,
                hit_points: cachedCharacter ? cachedCharacter.hit_points : 10,
                strength: cachedCharacter ? cachedCharacter.strength : 10,
                intelligence: cachedCharacter ? cachedCharacter.intelligence : 10,
                wisdom: cachedCharacter ? cachedCharacter.wisdom : 10,
                dexterity: cachedCharacter ? cachedCharacter.dexterity : 10,
                constitution: cachedCharacter ? cachedCharacter.constitution : 10,
                charisma: cachedCharacter ? cachedCharacter.charisma : 10,
                armor_class: cachedCharacter ? cachedCharacter.armor_class : 10
            };

            // Make API request to get full character details
            console.log(`Making API request for character ${id}`);
            try {
                const response = await fetch(`/api/characters/${id}`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (!response.ok) {
                    console.warn(`API error: ${response.status} - ${response.statusText}`);

                    // If we failed but have cached data, use that
                    if (cachedCharacter) {
                        console.warn("Using cached character data due to API error");
                        updateCharacterInfo(cachedCharacter);
                        displayMessage("Using cached character data. Some information may be out of date.", "system");
                        return true; // Return success, we can use the cached data
                    }

                    // If this is our first retry, try again
                    if (retryCount < 2) {
                        console.log(`Retrying character load (attempt ${retryCount + 1})`);
                        // Wait a short time before retrying
                        await new Promise(resolve => setTimeout(resolve, 1000));
                        return loadCharacterData(id, retryCount + 1);
                    }

                    // If all retry attempts failed, use minimal data
                    console.warn("Using minimal character data as fallback");
                    updateCharacterInfo(minimumCharacterData);
                    displayMessage("Limited character data available. Some features may not work correctly.", "system");
                    return true;
                }

                const character = await response.json();
                console.log(`API returned character:`, character);

                // Merge with cached data if needed (API might return partial data)
                const mergedCharacter = {
                    ...minimumCharacterData,  // Start with minimum data
                    ...cachedCharacter,       // Add cached data if available
                    ...character              // Override with fresh data from API
                };

                // Update UI with character info
                console.log("Updating character info with:", mergedCharacter);
                updateCharacterInfo(mergedCharacter);

                // Also try to load inventory and journal, but don't fail if they error
                try {
                    await loadInventory(id);
                } catch (error) {
                    console.warn("Error loading inventory, continuing:", error);
                }

                try {
                    await loadJournal(id);
                } catch (error) {
                    console.warn("Error loading journal, continuing:", error);
                }

                return true;
            } catch (apiError) {
                console.error("API error:", apiError);

                // If we have cached data, use it
                if (cachedCharacter) {
                    console.warn("Using cached character data due to API error");
                    updateCharacterInfo(cachedCharacter);
                    displayMessage("Using cached character data due to connection issues.", "system");
                    return true;
                }

                // If all else fails, use minimal data
                console.warn("Using minimal character data as fallback");
                updateCharacterInfo(minimumCharacterData);
                displayMessage("Limited character data available. Some features may not work correctly.", "system");
                return true;
            }
        } catch (error) {
            console.error("Error loading character data:", error);

            // Look for cached character data as a fallback
            if (characters && characters.length > 0) {
                const cachedCharacter = characters.find(c => String(c.id) === String(id));
                if (cachedCharacter) {
                    console.warn("Using cached character data due to API error");
                    updateCharacterInfo(cachedCharacter);
                    displayMessage("Using cached character data. Some information may be out of date.", "system");
                    return true; // Still consider this success since we have some data
                }
            }

            // If this is our first retry, try again
            if (retryCount < 2) {
                console.log(`Retrying character load after error (attempt ${retryCount + 1})`);
                // Wait a short time before retrying
                await new Promise(resolve => setTimeout(resolve, 1000));
                return loadCharacterData(id, retryCount + 1);
            }

            // Create minimal character data as last resort
            const minimumCharacterData = {
                id: id,
                name: `Character ${id}`,
                race: "Unknown",
                character_class: "Fighter",
                level: 1,
                hit_points: 10,
                strength: 10,
                intelligence: 10,
                wisdom: 10,
                dexterity: 10,
                constitution: 10,
                charisma: 10,
                armor_class: 10
            };

            console.warn("Using minimal character data as last resort");
            updateCharacterInfo(minimumCharacterData);
            displayMessage("Limited emergency character data loaded. Game functionality may be limited.", "system");
            return true;
        }
    }

    // Start the game
    initGame();
});

// Function to save journal entry to backend API
async function saveJournalEntryToAPI(characterId, text) {
    try {
        const response = await fetch('/journal/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                character_id: characterId,
                text: text
            })
        });

        if (!response.ok) {
            throw new Error('Failed to save journal entry to server');
        }

        return await response.json();
    } catch (error) {
        console.error('Error saving journal entry to API:', error);
        // Fall back to local storage if API fails
        saveJournalEntryToLocalStorage({
            date: new Date().toLocaleString(),
            text: text
        });
    }
}
