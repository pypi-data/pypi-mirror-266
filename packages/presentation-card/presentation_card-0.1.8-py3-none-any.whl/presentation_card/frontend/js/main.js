function sendValue(value) {
  Streamlit.setComponentValue(value)
}

function addHTMLtext(image_path, name, post, description) {
  var html_text = `
  <div class="image">
      <img src="{image_path}" class="profile-img">
  </div>
  <div class="content">
      <h1 class="title">Olá, me chamo <mark class="name">{name}</mark> <br>e sou <mark class="post">{post}</mark>.</h2>
      <p class="description" id="description">{description}</p>
      <button class="button_1" id="saiba_mais" onclick="handleClick(this)">Saiba mais</button>
      <button class="button_2" id="contatar" onclick="handleClick(this)">Contatar</button>
      <button type="submit" onclick="window.open('https://github.com/AbraaoAndrade/portfolio_streamlit_sharing/raw/4aa709f7878567afd762e18750f2cece57cc5808/data/CV_abraao_andrade_2024.pdf')" class="button_3" >Baixar CV</button>
  </div>
  `;
  html_text = html_text.replace("{image_path}", image_path);
  html_text = html_text.replace("{name}", name);
  html_text = html_text.replace("{post}", post);
  html_text = html_text.replace("{description}", description);
  
  document.querySelector('.center').insertAdjacentHTML(
    'afterbegin',
    html_text     
  )
}

function handleClick(component){
  sendValue(component.id);
}

var first_run = true;

function onRender(event) {
  if (first_run) {
    var {image_path, name, post, description} = event.detail.args;

    addHTMLtext(image_path, name, post, description);

    first_run = false;
  }

  if (!window.rendered) {
    window.rendered = true
  }
}


Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender)
Streamlit.setComponentReady()
Streamlit.setFrameHeight(300)
Streamlit.setFrameWidth(704)
