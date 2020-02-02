var countdownInterval;
var lobbyElement = document.getElementById('lobby');
var hostnameElement = document.getElementById('hostname');
var lobbyCtaElement = document.getElementById('lobby-cta');
var categoriesElement = document.getElementById('categories');
var categoryChooserElement = document.getElementById('category-chooser');
var favouriteChooserElement = document.getElementById('favourite-chooser');
var categoriesListElement = document.getElementById('category-choices');
var promptElement = document.getElementById('prompt');
var promptOpenElement = document.getElementById('prompt-open');
var promptClosedElement = document.getElementById('prompt-closed');
var restartElement = document.getElementById('restart-ui');
var productElement = document.getElementById('product');
var categoryElement = document.getElementById('category');
var versionElement = document.getElementById('version');
var timerElement = document.getElementById('timer');
var changesElement = document.getElementById('changes');
var bossElement = document.getElementById('boss');
var subtitleElement = document.getElementById('subtitle');
var showSessionCodeElement = document.getElementById('show-session-code');
var hideSessionCodeElement = document.getElementById('hide-session-code');
var sessionCodeElement = document.getElementById('session-code');
var sessionCodePlaceholderElement = document.getElementById('session-code-placeholder');
var robotHasBeenIntroduced = false;
var roundHasBeenIntroduced = false;
var currentPlayerUUID;
var currentPlayerName;

var ROUND_LENGTH = 60;  // in seconds
var MOODS = ['neutral', 'crossed', 'frown', 'point'];

var VO = {
  A: [
    {n: '1'},
    {n: '2'},
    {n: '3'},
    {n: '4'},
    {n: '5'}],
  B: [
    {n: '1'},
    {n: '2'},
    {n: '3'},
    {n: '4'},
    {n: '5'}],
  C: [
    {n: '1'},
    {n: '2'},
    {n: '3'},
    {n: '4'},
    {n: '5'}],
  D: [{n: ''}],
  E: [
    {n: '1'},
    {n: '2'},
    {n: '3'},
    {n: '4'},
    {n: '5'}],
  F: [
    {n: '1'},
    {n: '2'},
    {n: '3'},
    {n: '4'},
    {n: '5'},
    {n: '6'},
    {n: '7'},
    {n: '8'},
    {n: '9'},
    {n: '10'}],
  G: [
    {n: '1'},
    {n: '2'},
    {n: '3'},
    {n: '4'}],
  H: [
    {n: '1'},
    {n: '2'},
    {n: '3'},
    {n: '4'},
    {n: '5'},
    {n: '6'},
    {n: '7'},
    {n: '8'},
    {n: '9'}]};

function playAudioFrom(cat, callback) {
  var selected = VO[cat][Math.floor(Math.random() * VO[cat].length)];
  function doCallback() {
    hideSubs();
    selected.audio.removeEventListener('ended', doCallback);
    if (callback) callback();
  }
  showSubs(selected.transcript);
  selected.audio.addEventListener('ended', doCallback);
  selected.audio.play();
}

function showSubs(phrase) {
  subtitleElement.textContent = phrase;
  subtitleElement.style.removeProperty('display');
}

function hideSubs() {
  subtitleElement.style.setProperty('display', 'none');
}

function speak(phrase) {
  showSubs(phrase);
  meSpeak.speak(phrase, {}, hideSubs);
}

function hideEverything() {
  lobbyCtaElement.style.setProperty('display', 'none');
  categoriesElement.style.setProperty('display', 'none');
  promptElement.style.setProperty('display', 'none');
  restartElement.style.setProperty('display', 'none');
}

function api(endpoint, params, callback) {
  var xhr = new XMLHttpRequest();
  var formData = new FormData();
  if (params) {
    for (var key in params) {
      formData.append(key, params[key]);
    }
  }
  xhr.addEventListener('load', callback);
  xhr.open('post', endpoint);
  xhr.send(formData);
}

function animateBoss() {
  bossElement.setAttribute('data-mood', MOODS[Math.floor(Math.random() * MOODS.length)]);
  setTimeout(animateBoss, 1000 + Math.random() * 2000);
}

function startRound(event) {
  var winnerUUID;

  if (event) {
    event.preventDefault();
    winnerUUID = event.currentTarget.getAttribute('data-player');
  }

  hideEverything();

  api('/_categories', {
    winner: winnerUUID || '',
    judge: currentPlayerUUID || ''
  }, function() {
    if (this.status !== 200) {
      lobbyCtaElement.style.removeProperty('display');
      alert(this.responseText);
      return;
    }
    var response = JSON.parse(this.responseText);
    if (response.message) alert(response.message);
    categoriesElement.style.removeProperty('display');
    categoriesListElement.innerHTML = '';
    var categories = response.categories;
    currentPlayerUUID = response.player.uuid;
    currentPlayerName = response.player.name;
    categoryChooserElement.innerText = currentPlayerName;
    favouriteChooserElement.innerText = currentPlayerName;

    for (var i = 0; i < categories.length; i++) {
      var categoryListItem = document.createElement('li');
      var categoryLink = document.createElement('a');
      categoryLink.setAttribute('href', '#');
      categoryLink.addEventListener('click', chooseCategory);
      categoryLink.appendChild(document.createTextNode(categories[i]));
      categoryListItem.appendChild(categoryLink);
      categoriesListElement.appendChild(categoryListItem);
    }

    if (roundHasBeenIntroduced) playAudioFrom('F');
    else {
      roundHasBeenIntroduced = true;
      playAudioFrom('A', function() {
        playAudioFrom('B', function() {
          playAudioFrom('C');
        });
      });
    }
  });
}

function chooseCategory(event) {
  event.preventDefault();
  hideEverything();
  changesElement.style.setProperty('display', 'none');
  changesElement.innerHTML = '';
  promptOpenElement.style.setProperty('display', 'none');
  promptClosedElement.style.setProperty('display', 'none');

  api('_prompt', {category: event.currentTarget.innerText}, function() {
    promptElement.style.removeProperty('display');
    promptOpenElement.style.removeProperty('display');
    product = JSON.parse(this.responseText);
    productElement.innerText = product.name;
    categoryElement.innerText = product.category;
    versionElement.innerText = product.version;
    function doRobotSpeech() {
      if (product.comment !== undefined) {
        speak(product.name + ', version ' + product.version + '. ' + product.comment);
      }
    }
    if (robotHasBeenIntroduced) doRobotSpeech();
    else {
      robotHasBeenIntroduced = true;
      playAudioFrom('D', function() { playAudioFrom('E', doRobotSpeech); });
    }

    var countdown = ROUND_LENGTH;

    function decrement() {
      if (countdown === 0) {
        promptOpenElement.style.setProperty('display', 'none');
        promptClosedElement.style.removeProperty('display');
        clearInterval(countdownInterval);
        changesElement.style.removeProperty('display');
        api('/_entries', {}, function() {
          var response = JSON.parse(this.responseText);
          var entries = response.entries;
          for (var i = 0; i < entries.length; i++) {
            var entryElement = document.createElement('li');
            var entryLink = document.createElement('a');
            entryLink.setAttribute('data-player', entries[i].uuid);
            entryLink.appendChild(document.createTextNode(entries[i].entry));
            if (entries[i].uuid !== currentPlayerUUID) {
              entryLink.setAttribute('href', '#');
              entryLink.addEventListener('click', startRound);
            }
            entryElement.appendChild(entryLink);
            changesElement.appendChild(entryElement);
          }

          restartElement.style.removeProperty('display');
        });
      }
      timerElement.innerText = countdown.toString(10);
      countdown--;
    }
    countdownInterval = setInterval(decrement, 1000);
    decrement();
  });
}

function beginGatheringPlayers() {
  hideEverything();
  animateBoss();

  hostnameElement.innerText = window.location.host;
  subtitleElement.style.setProperty('display', 'none');
  lobbyCtaElement.style.removeProperty('display');

}

function annotateVoiceWithScript() {
  var lines = this.responseText.split('\n');
  var section;
  var sectionIndex = 0;
  for (var i = 0; i < lines.length; i++) {
    if (lines[i]) {
      if (lines[i][0] === '#') {
        section = lines[i].slice(1);
        sectionIndex = 0;
      } else {
        var part = VO[section][sectionIndex];
        if (part) part.transcript = lines[i];
        sectionIndex++;
      }
    }
  }
}

function preloadVO() {
  for (var cat in VO) {
    for (var i = 0; i < VO[cat].length; i++) {
      var line = VO[cat][i];
      line.audio = new Audio('/static/voiceover/' + cat + line.n + '.mp3');
    }
  }

  var scriptXhr = new XMLHttpRequest();
  scriptXhr.addEventListener('load', annotateVoiceWithScript);
  scriptXhr.open('get', '/static/voiceover/script.txt');
  scriptXhr.send();
}

function showSessionCode() {
  hideSessionCodeElement.style.removeProperty('display');
  sessionCodeElement.style.setProperty('display', 'inline');

  showSessionCodeElement.style.setProperty('display', 'none');
  sessionCodePlaceholderElement.style.setProperty('display', 'none');
}

function hideSessionCode() {
  showSessionCodeElement.style.removeProperty('display');
  sessionCodePlaceholderElement.style.setProperty('display', 'inline');

  hideSessionCodeElement.style.setProperty('display', 'none');
  sessionCodeElement.style.setProperty('display', 'none');
}

meSpeak.loadVoice('en/en');
beginGatheringPlayers();
preloadVO();
