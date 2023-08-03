let ws = new WebSocket('ws://localhost:8000/game/ws');
let main = document.getElementById('main');


ws.onopen = function (event) {
    console.log(event);
}

ws.onmessage = function (event) {
    let data = JSON.parse(event.data);
    console.log(data);
    switch (data.action) {
        case 'error':
            alert(data.detail);
            break;
        case 'get_all':
            getMainPage(data);
            break;
        case 'create':
            getGamePage(data);
            break;
        case 'join':
            getGamePage(data);
            break;
        default:
            console.log(data)
            break;
    }
}

function send(data) {
    ws.send(JSON.stringify(data));
}

function createGame(event) {
    send({'action': 'create'});
}

function getGameList(event) {
    send({'action': 'get_list'});
}

function closeGame(event) {
    send({'action': 'close'});
}

function joinGame(event) {
    send({'action': 'join', 'game_number': event.target.dataset.number});
}

function setReady(event) {
    let divStatements = event.target.closest('div');
    if (divStatements.dataset.state) {
        send(
            {
                'action': 'ready',
                'state': divStatements.dataset.state,
                'game_number': document.getElementById('game-info').number,
            }
        );
    } else {
        alert('Choose your item!');
    }
}

document.getElementById('create-game').addEventListener('click', createGame);
document.getElementById('get-game-list').addEventListener('click', getGameList);


function getMainPage(data) {
    let gameList = data.game_list;
            let noGames = document.getElementById('no-games');
            noGames.innerHTML = '';
            if (gameList.length === 0) {
                let div = document.createElement('div');
                let text = document.createTextNode('No active games now, you can create own if you want it');
                div.appendChild(text);
                noGames.appendChild(div);
                return null;
            }
            let gameListUl = document.getElementById('game-list');
            gameListUl.innerHTML = '';
            gameList.forEach((gameInfo) => {
                let li = document.createElement('li');
                li.classList.add('game-list');
                let text = document.createTextNode(`${gameInfo.game_number} `);
                let span = document.createElement('span');
                span.innerHTML = gameInfo.author_username;
                let btn = document.createElement('button');
                btn.innerHTML = 'join';
                btn.id = 'join-game';
                btn.setAttribute('data-number', gameInfo.game_number);
                li.appendChild(text);
                li.appendChild(span);
                li.appendChild(btn);
                gameListUl.appendChild(li);
                btn.addEventListener('click', joinGame);
            });
}

function getGamePage(data) {
    main.innerHTML = '';

    let gameInfo = document.createElement('div');
    gameInfo.id = 'game-info';
    gameInfo.dataset.number = data.game_info.game_number;
    let gameInfoText = document.createTextNode(`Game number #${data.game_info.game_number}`);
    gameInfo.appendChild(gameInfoText);

    let isReady = document.createElement('div');
    let readyText;
    if (data.game_info.is_init_player_ready) {
        readyText = document.createTextNode('Player is ready');
    } else {
        readyText = document.createTextNode('Player is not ready yet');
    }
    isReady.appendChild(readyText);

    let div = document.createElement('div');
    let text = document.createTextNode('Choose your item');
    div.appendChild(text);

    let items = createStatements();


    main.appendChild(gameInfo);
    main.appendChild(isReady);
    main.appendChild(div);
    main.appendChild(items);
}

function createStatements () {
    let items = document.createElement('div');
    items.id = 'items';

    let readyBtn = document.createElement('button');
    readyBtn.classList.add('content-center');
    readyBtn.addEventListener('click', setReady);
    let readyBtnText = document.createTextNode('Im Ready!');
    readyBtn.appendChild(readyBtnText);

    let rock = document.createElement('input');
    rock.setAttribute('type', 'image');
    rock.setAttribute('src', '/static/png/rock.png');
    rock.dataset.state = 'rock';
    rock.classList.add('game-icon');
    rock.addEventListener('click', setState);

    let paper = document.createElement('input');
    paper.setAttribute('type', 'image');
    paper.setAttribute('src', '/static/png/paper.png');
    paper.dataset.state = 'paper';
    paper.classList.add('game-icon');
    paper.addEventListener('click', setState);

    let scissors = document.createElement('input');
    scissors.setAttribute('type', 'image');
    scissors.setAttribute('src', '/static/png/scissors.png');
    scissors.dataset.state = 'scissors';
    scissors.classList.add('game-icon');
    scissors.addEventListener('click', setState);

    items.appendChild(rock);
    items.appendChild(paper);
    items.appendChild(scissors);
    items.appendChild(readyBtn);
    return items;
}

function setState(event) {
    let current_state = event.target.dataset.state;
    let divStatements = event.target.closest('div');

    children = divStatements.childNodes;
    children.forEach((child) => {
        if (child.hasAttribute('style')) {
            child.removeAttribute('style');
        }
    });
    divStatements.dataset.state = current_state;
    event.target.style.border = 'solid #00FF8A';
    event.target.style.borderRadius = '100%';

}