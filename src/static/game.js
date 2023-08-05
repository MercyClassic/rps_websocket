let ws = new WebSocket('ws://localhost:8000/game/ws');
let main = document.getElementById('main');


ws.onmessage = function (event) {
    let data = JSON.parse(event.data);
    switch (data.action) {
        case 'error':
            alert(data.detail);
            break;
        case 'get_all':
            getMainPage(data);
            break;
        case 'first_ten':
            getMainPage(data, true);
            break;
        case 'create':
        case 'join':
            getGamePage(data);
            break;
        case 'ready':
            changeReadyStatusVisibility();
            break;
        case 'win':
        case 'lose':
        case 'draw':
            waitingForResult(data.action);
            break
//        case 'win':
//            getWinPage();
//            break;
//        case 'lose':
//            getLosePage();
//            break;
//        case 'draw':
//            getDrawPage();
//            break;
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
                'game_number': document.getElementById('game-info').dataset.number,
            }
        );
    } else {
        alert('Choose your item!');
    }
}

document.getElementById('create-game').addEventListener('click', createGame);


function getMainPage(data, first_ten = false) {
    let gameList = data.game_list;
    let noGames = document.getElementById('no-games');
    if (noGames === null) {
        return null;
    }
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

    if (first_ten) {
        if (document.getElementById('get-game-list') !== null) {
            return null;
        }
        let showMoreGames = document.createElement('button');
        showMoreGames.id = 'get-game-list';
        let text = document.createTextNode('show more games');
        showMoreGames.appendChild(text);
        document.getElementById('games').appendChild(showMoreGames);
        showMoreGames.addEventListener('click', getGameList);
    } else {
        document.getElementById('get-game-list').remove();
    }
}

function getGamePage(data) {
    main.innerHTML = '';

    let gameInfo = document.createElement('div');
    gameInfo.id = 'game-info';
    gameInfo.dataset.number = data.game_info.game_number;
    let gameInfoText = document.createTextNode(`Game number #${data.game_info.game_number}`);
    gameInfo.appendChild(gameInfoText);

    let isReady = document.createElement('div');
    isReady.id = 'is-ready-text';
    let readyText;
    if (data.game_info.is_init_player_ready) {
        readyText = document.createTextNode('Another player is ready');
    } else {
        readyText = document.createTextNode('Another player is not ready yet');
    }
    isReady.appendChild(readyText);

    let div = document.createElement('div');
    let text = document.createTextNode('Choose your item');
    div.appendChild(text);

    let statements = createStatements();

    main.appendChild(gameInfo);
    main.appendChild(isReady);
    main.appendChild(div);
    main.appendChild(statements);
}

function createStatements () {
    let statements = document.createElement('div');
    statements.id = 'statements';

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

    statements.appendChild(rock);
    statements.appendChild(paper);
    statements.appendChild(scissors);
    statements.appendChild(readyBtn);
    return statements;
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

function changeReadyStatusVisibility() {
    let btn = document.getElementById('is-ready-text');
    btn.innerHTML = 'Another player is ready';
}

let time;
let timerValue;
let timer;
let interval;

function waitingForResultPromise() {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            resolve();
        }, 3500);
    })
}

function resultTimer() {
    time--;
    if (time === 0) {
        clearInterval(interval);
    }
    timerValue.innerHTML = time;
    timer.appendChild(timerValue);
}

function waitingForResult(action) {
    main.innerHTML = '';
    time = 3;
    timer = document.createElement('div');

    let text = document.createElement('div');
    text.id = 'timer-text';
    text.innerHTML = 'Waiting for result...';
    text.classList.add('content-center');
    text.style.fontSize = '26px';

    timerValue = document.createElement('span');
    timerValue.id = 'timer-value';
    timerValue.innerHTML = '3';
    timerValue.classList.add('content-center');
    timerValue.style.fontSize = '26px';

    interval = setInterval(resultTimer, 1000);
    timer.appendChild(text);
    timer.appendChild(timerValue);
    main.appendChild(timer);
    waitingForResultPromise().then(() => {
        switch (action) {
            case 'win':
                getWinPage();
                break;
            case 'lose':
                getLosePage();
                break;
            case 'draw':
                getDrawPage();
                break;
        }
    })
}

function getWinPage() {
    main.innerHTML = '';
    let win = document.createElement('div');
    let winText = document.createTextNode('You are winner!');
    win.appendChild(winText);
    win.classList.add('win-text');
    main.appendChild(win);
}

function getLosePage() {
    main.innerHTML = '';
    let lose = document.createElement('div');
    let loseText = document.createTextNode('You are loser!');
    lose.appendChild(loseText);
    lose.classList.add('lose-text');
    main.appendChild(lose);
}

function getDrawPage() {
    main.innerHTML = '';
    let draw = document.createElement('div');
    let drawText = document.createTextNode('Friendly draw!');
    draw.appendChild(drawText);
    draw.classList.add('draw-text');
    main.appendChild(draw);
}
