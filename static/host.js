var lobbyElement = document.getElementById('lobby');
var categoriesElement = document.getElementById('categories');
var categoriesListElement = document.getElementById('category-choices');
var promptElement = document.getElementById('prompt');
var productElement = document.getElementById('product');
var versionElement = document.getElementById('version');

function hideEverything() {
  lobbyElement.style.setProperty('display', 'none');
  categoriesElement.style.setProperty('display', 'none');
  promptElement.style.setProperty('display', 'none');
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

function everyoneIsHere() {
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

  api('_prompt', {category: event.currentTarget.innerText}, function() {
    promptElement.style.removeProperty('display');
    product = JSON.parse(this.responseText);
    productElement.innerText = product.name;
    versionElement.innerText = product.version;
    if (product.comment) {
      console.log(product.comment);
    }
  });
}

function beginGatheringPlayers() {
  hideEverything();
  lobbyElement.style.removeProperty('display');
}

beginGatheringPlayers();
