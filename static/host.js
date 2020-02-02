var countdownInterval;
var lobbyElement = document.getElementById('lobby');
var hostnameElement = document.getElementById('hostname');
var lobbyCtaElement = document.getElementById('lobby-cta');
var categoriesElement = document.getElementById('categories');
var categoriesListElement = document.getElementById('category-choices');
var promptElement = document.getElementById('prompt');
var promptOpenElement = document.getElementById('prompt-open');
var restartElement = document.getElementById('restart-ui');
var productElement = document.getElementById('product');
var categoryElement = document.getElementById('category');
var versionElement = document.getElementById('version');
var timerElement = document.getElementById('timer');
var changesElement = document.getElementById('changes');
var bossElement = document.getElementById('boss');
var subtitleElement = document.getElementById('subtitle');

var ROUND_LENGTH = 60;  // in seconds
var MOODS = ['neutral', 'crossed', 'frown', 'point'];

function speak(phrase) {
  subtitleElement.textContent = phrase;
  subtitleElement.style.removeProperty('display');
  meSpeak.speak(phrase, {}, function() {
    subtitleElement.style.setProperty('display', 'none');
  });
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

function startRound() {
  hideEverything();

  api('/_categories', {}, function() {
    categoriesElement.style.removeProperty('display');
    categoriesListElement.innerHTML = '';
    categories = JSON.parse(this.responseText);

    for (var i = 0; i < categories.length; i++) {
      var categoryListItem = document.createElement('li');
      var categoryLink = document.createElement('a');
      categoryLink.setAttribute('href', '#');
      categoryLink.addEventListener('click', chooseCategory);
      categoryLink.appendChild(document.createTextNode(categories[i]));
      categoryListItem.appendChild(categoryLink);
      categoriesListElement.appendChild(categoryListItem);
    }
  });
}

function chooseCategory(event) {
  event.preventDefault();
  hideEverything();
  changesElement.style.setProperty('display', 'none');
  changesElement.innerHTML = '';
  promptOpenElement.style.setProperty('display', 'none');

  api('_prompt', {category: event.currentTarget.innerText}, function() {
    promptElement.style.removeProperty('display');
    promptOpenElement.style.removeProperty('display');
    product = JSON.parse(this.responseText);
    productElement.innerText = product.name;
    categoryElement.innerText = product.category;
    versionElement.innerText = product.version;
    if (product.comment !== undefined) {
      speak(product.name + ', version ' + product.version + '. ' + product.comment);
    }

    var countdown = ROUND_LENGTH;

    function decrement() {
      if (countdown === 0) {
        promptOpenElement.style.setProperty('display', 'none');
        clearInterval(countdownInterval);
        changesElement.style.removeProperty('display');
        api('/_entries', {}, function() {
          var entries = JSON.parse(this.responseText);
          for (var i = 0; i < entries.length; i++) {
            var entryElement = document.createElement('li');
            entryElement.appendChild(document.createTextNode(entries[i].entry));
            var attributionElement = document.createElement('em');
            attributionElement.appendChild(document.createTextNode('-' + entries[i].name));
            entryElement.appendChild(document.createTextNode(' '));
            entryElement.appendChild(attributionElement);
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

meSpeak.loadVoice('en/en');
beginGatheringPlayers();
