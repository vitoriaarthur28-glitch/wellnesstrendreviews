/* Chat com especialista do nicho (v34): roteiro fixo da conversa (referencia/chat/roteiro_chat.md) + perguntas livres por palavra-chave.
   Tudo o que ele diz vem dos campos CHAT_* e da própria página (fatos do site oficial). Nada sai da página; o nome fica só nesta conversa. */
document.addEventListener("DOMContentLoaded", function(){
  var lanc = document.getElementById("chat-lancador"), jan = document.getElementById("chat-janela"),
      lista = document.getElementById("chat-msgs"), form = document.getElementById("chat-form"),
      campo = document.getElementById("chat-campo"), fechar = document.getElementById("chat-fechar"),
      modelo = document.getElementById("chat-respostas"), oferta = document.getElementById("chat-oferta"),
      banner = document.getElementById("consentimento"), selo = document.getElementById("chat-selo");
  if (!lanc || !jan || !modelo) return;
  var produto = document.getElementById("chat-nome-produto").getAttribute("data-produto");
  var espec = document.getElementById("chat-nome-produto").textContent.trim().toLowerCase();
  var pessoa = document.getElementById("chat-nome-pessoa").textContent.trim();
  var subidChat = oferta ? (oferta.getAttribute("data-subid-chat") || "") : "";
  var reduz = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var nome = "", passo = "nome", iniciou = false, ocupado = false, ofertaMostrada = false, pendente = false, compraAvisada = false, timerSumiu = null;
  var resp = { tempo: "", dor: "", tentou: null };
  function esc(t){ var d = document.createElement("div"); d.textContent = t; return d.innerHTML; }
  function hora(){ var d = new Date(); return ("0"+d.getHours()).slice(-2) + ":" + ("0"+d.getMinutes()).slice(-2); }
  function rolar(){ lista.scrollTop = lista.scrollHeight; }
  function txt(ch){ var el = modelo.content.querySelector('[data-r="'+ch+'"]'); return el ? el.innerHTML.replace(/\{nome\}/g, esc(nome)).trim() : ""; }
  function baloes(html){ var d = document.createElement("div"); d.innerHTML = html; var ps = d.querySelectorAll("p"); if (!ps.length) return html ? [html] : []; return [].map.call(ps, function(p){ return p.outerHTML; }); }
  function bolha(conteudo, eu){
    var m = document.createElement("div"); m.className = "chat-msg " + (eu ? "eu" : "ela");
    if (conteudo && conteudo.nodeType) { m.className = "chat-msg ela " + (conteudo.classList.contains("chat-destaque") ? "destaque" : "cartoes"); m.appendChild(conteudo); lista.appendChild(m); rolar(); chegou(); return; }
    var b = document.createElement("div"); b.className = "bolha";
    if (eu) { var p = document.createElement("p"); p.textContent = conteudo; b.appendChild(p); } else { b.innerHTML = conteudo; }
    var h = document.createElement("span"); h.className = "hora"; h.textContent = hora(); b.appendChild(h);
    m.appendChild(b); lista.appendChild(m); rolar();
    if (!eu) chegou();
  }
  /* Cada mensagem dela: som de mensagem recebida; com o chat fechado, conta como não lida no selo vermelho */
  var naoLidas = 0;
  function chegou(){
    tocarMsg();
    if (jan.hidden && iniciou) { naoLidas++; mostrarSelo(); if (typeof mostrarBalao === "function") mostrarBalao(); }
  }
  function fala(partes, depois){
    ocupado = true; var i = 0;
    (function proxima(){
      if (i >= partes.length) { ocupado = false; if (depois) depois(); return; }
      var item = partes[i++];
      /* Ritmo humano: pausa curta (como quem lê) e "digitando" proporcional ao tamanho da mensagem */
      var pausa = reduz ? 0 : 600;
      var tempo = reduz ? 250 : Math.min(3400, 1200 + (typeof item === "string" ? item.replace(/<[^>]+>/g, "").length * 15 : 800));
      setTimeout(function(){
        var t = document.createElement("div"); t.className = "chat-msg ela digitando";
        t.innerHTML = '<div class="bolha"><span></span><span></span><span></span></div>';
        lista.appendChild(t); rolar();
        setTimeout(function(){ t.remove(); if (item === "#divisor") { var dv = document.createElement("p"); dv.className = "chat-divisor"; dv.textContent = "Claim your offer"; lista.appendChild(dv); } else { bolha(item, false); } proxima(); }, tempo);
      }, pausa);
    })();
  }
  function focar(){ if (!jan.hidden) campo.focus(); }
  function ehNao(t){ t = t.trim().toLowerCase(); return /^(no|nope|nah|not|never|nothing|none)\b/.test(t) || /\b(haven't|have not|never tried|not yet|no thanks|don't|do not|not really|not interested|not now|not today|maybe later|later|not sure|i'll think|let me think|need to think|think about it)\b/.test(t); }
  /* ---------- Leitura das respostas (resumo e recomendação) ---------- */
  var NUM = "(\\d+|a few|a couple of|a couple|several|many|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|an|a)";
  function lerTempo(t){
    t = t.toLowerCase();
    var m = t.match(new RegExp("\\b(about |almost |over |more than |around )?" + NUM + "\\s+(days?|weeks?|months?|years?)\\b"));
    if (m) {
      var qtd = m[2], uni = m[3], n = parseInt(qtd, 10);
      var palavras = {a:1,an:1,one:1,two:2,three:3,four:4,five:5,six:6,seven:7,eight:8,nine:9,ten:10,eleven:11,twelve:12};
      if (isNaN(n)) n = palavras[qtd] || (/several|many/.test(qtd) ? 4 : 2);
      var longo = /year/.test(uni) || (/month/.test(uni) && n >= 6);
      return { frase: m[0].trim(), longo: longo, conhecido: true };
    }
    if (/\b(years|decades?|long time|ages|forever|since i was|whole life|as long as i can remember)\b/.test(t)) return { frase: "a long time", longo: true, conhecido: true };
    if (/\b(recent|recently|just started|lately|new|last week|last month|this year)\b/.test(t)) return { frase: "", recente: true, longo: false, conhecido: true };
    return { frase: "", longo: true, conhecido: false };
  }
  function lerDores(t){
    var achadas = [], el = modelo.content.querySelector('[data-r="dores-chaves"]');
    if (!el) return achadas;
    el.textContent.split("|").forEach(function(par){
      var p = par.split("="); if (p.length !== 2) return;
      var chaves = p[0].split(","), frase = p[1].trim();
      if (chaves.some(function(c){ c = c.trim().replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); return c && new RegExp("\\b" + c + "(s|es)?\\b", "i").test(t); }) && achadas.indexOf(frase) === -1) achadas.push(frase);
    });
    return achadas;
  }
  function juntar(itens){ return itens.length < 2 ? (itens[0] || "") : itens.slice(0, -1).join(", ") + " and " + itens[itens.length - 1]; }
  /* As palavras da própria pessoa (curtas), quando nenhuma chave do nicho bate */
  function proprias(t){ t = (t || "").replace(/[.!?]+$/, "").trim(); if (t.length < 3 || t.length > 90 || /^(yes|yeah|yep|no|nope|idk|i don'?t know|not sure|nothing)\b/i.test(t)) return ""; return t.charAt(0).toLowerCase() + t.slice(1); }
  function resumo(){
    var partes = [], tp = lerTempo(resp.tempo), dores = lerDores(resp.dor);
    if (tp.frase) partes.push("you've been dealing with this for " + esc(tp.frase));
    else if (tp.recente) partes.push("this started more recently");
    if (dores.length) partes.push("what bothers you most is " + esc(juntar(dores)));
    else if (proprias(resp.dor)) partes.push("what bothers you most is \u201c" + esc(proprias(resp.dor)) + "\u201d");
    if (resp.tentou === true) partes.push("you've already tried other things");
    if (resp.tentou === false) partes.push("this is your first time looking for a solution");
    if (!partes.length) return "<p>So, " + esc(nome) + ", based on everything you told me, here's what makes sense for you.</p>";
    return "<p>So, " + esc(nome) + ", just to make sure I got it right: " + juntar(partes) + ".</p>";
  }
  /* ---------- Cartões: todas as opções, com a recomendada marcada ---------- */
  function cartoes(recomendado){
    var c = oferta.cloneNode(true); c.removeAttribute("id");
    c.querySelectorAll("a[href]").forEach(function(a){
      if (subidChat) { try { var u = new URL(a.href); u.searchParams.set(subidChat, "chat"); a.href = u.toString(); } catch(e){} }
    });
    if (recomendado) {
      var alvo = c.querySelector('.chat-cartao[data-pacote="' + recomendado + '"]');
      if (alvo) { alvo.classList.add("recomendado"); var tag = document.createElement("span"); tag.className = "tag-recomendado"; tag.textContent = "★ Recommended for you"; alvo.insertBefore(tag, alvo.firstChild); }
    }
    return c;
  }
  /* ---------- Conversa guiada (estrutura fixa) ----------
     Cada etapa guarda a pergunta da vez (pergunta) para poder repeti-la depois de responder uma objeção no meio do roteiro. */
  var pergunta = [], chegouOferta = false;
  function perguntar(novoPasso, antes, pq){ passo = novoPasso; pergunta = pq; fala(antes.concat(pq), focar); }
  function ehSim(t){ t = t.trim().toLowerCase(); return /^(yes|yeah|yep|yup|ya|sure|ok|okay|of course|please|definitely|absolutely|certainly|go ahead|show me|let's see|y)\b/.test(t) || /\b(yes|sure|please)\b/.test(t); }
  var ROTEIRO = {
    tempo: function(){
      perguntar("tempo", ["<p>Hello " + esc(nome) + "! I'm " + esc(pessoa) + ", a " + esc(espec) + ". I'm here to help you with " + esc(produto) + ". 😊</p>"],
                ["<p>" + txt("pergunta-tempo") + "</p>"]);
    },
    dor: function(){ perguntar("dor", [], baloes(txt("pergunta-dor"))); },
    tentou: function(){ perguntar("tentou", baloes(txt("empatia")), ["<p>" + txt("pergunta-tentou") + "</p>"]); },
    como: function(nao){
      perguntar("ingredientes", baloes(txt(nao ? "tentou-nao" : "tentou-sim")).concat(["<p>" + txt("gancho") + "</p>"], baloes(txt("sem-blend")), baloes(txt("como"))),
                ["<p>Would you like to know more about the specific ingredients and their doses?</p>"]);
    },
    ingredientes: function(nao){ perguntar("resultados", nao ? [] : baloes(txt("ingredientes-guia")), ["<p>Would you like to know how long it usually takes to start feeling results?</p>"]); },
    /* Depoimento em destaque: logo depois dos resultados (é quando a pessoa se pergunta se funciona); quem disse "não" aos
       resultados vê o destaque antes da pergunta da oferta. Aparece uma vez no roteiro. */
    resultados: function(nao){ perguntar("uso", nao ? [] : baloes(txt("resultados")).concat(temDepoimento() ? partesDepoimento() : []), ["<p>Would you like to know the best way to take it to get these results?</p>"]); },
    uso: function(nao){ perguntar("oferta", (nao ? [] : baloes(txt("uso-guia"))).concat((depoimentoMostrado || !temDepoimento()) ? [] : partesDepoimento()), ["<p>Since you've been looking for a solution, would you like to see the recommended options to get started?</p>"]); },
    oferta: function(nao){
      chegouOferta = true;
      if (nao) { recusou(); return; }
      mostrarOferta(true);
    }
  };
  /* Oferta: completa (resumo + cartões + recomendação + preço por dia + garantia + promoção) ou curta (depois de uma recusa:
     cartões + recomendação, sem repetir o que ela já ouviu) */
  function mostrarOferta(completa){
    passo = "livre"; pergunta = [];
    var tp = lerTempo(resp.tempo), rec = (tp.conhecido && !tp.longo) ? "2" : "3";
    var comPacotes = !!(oferta && oferta.querySelector('[data-pacote="' + rec + '"]'));
    /* Produto sem preços na página do link (um botão para o site oficial no lugar dos cartões): outras frases */
    var semPrecos = !!(oferta && !oferta.querySelector(".chat-cartao"));
    var abre = semPrecos ? "<p>Sure! The current packages and prices are on the official website. Here's the secure link:</p>"
                         : (completa ? "<p>Sure, let me show you all the options so you can compare:</p>" : "<p>Sure, " + esc(nome) + "! Here are all the options, no commitment:</p>");
    var partes = completa ? [resumo(), abre, "#divisor"] : [abre, "#divisor"];
    if (oferta) partes.push(cartoes(comPacotes ? rec : null));
    if (comPacotes) {
      /* Depois dos cartões: a recomendação volta às palavras da pessoa */
      var motivo = tp.frase ? "Since you've been dealing with this for " + esc(tp.frase) : (tp.recente ? "Since this started more recently" : "");
      partes.push("<p>" + (motivo ? motivo + ", here's my recommendation:" : "Here's my recommendation:") + "</p>");
      partes = partes.concat(baloes(txt(rec === "2" ? "recomenda-2" : "recomenda-3")));
      if (completa) partes = partes.concat(baloes(txt("preco-dia")));
    }
    if (completa) partes = partes.concat(baloes(txt("garantia-curta")), baloes(txt("promo")));
    partes.push(semPrecos ? "<p>Take a look whenever you're ready, " + esc(nome) + ". I'm here if you have any questions.</p>"
                          : "<p>Which one feels right for you, " + esc(nome) + "?</p>");
    ofertaMostrada = true;
    fala(partes, depoisDeFalar);
  }
  /* ---------- Recusa da oferta: pergunta o que está segurando, responde a objeção certa e oferece só ver os preços ---------- */
  var perguntouObjecao = false;
  function recusou(){
    passo = "objecao"; perguntouObjecao = true;
    pergunta = ["<p>Can I ask what's holding you back? Is it the price, whether it will really work for you, or something about safety? 😊</p>"];
    fala(["<p>No problem, " + esc(nome) + ".</p>"].concat(pergunta), depoisDeFalar);
  }
  var VER_PRECOS = "<p>Would you like to just take a look at the prices? No commitment 😊</p>";
  function tratarObjecao(t){
    var ch = tema(t);
    if (ch === "preco") ch = "caro";
    var partes = (ch === "nao-sei") ? ["<p>I completely understand, " + esc(nome) + ". There's no rush.</p>"].concat(baloes(txt("garantia-curta")))
                                    : (ch === "caro" ? ["<p>I understand, " + esc(nome) + ".</p>"] : []).concat(conteudo(ch));
    passo = "ver-precos"; pergunta = [VER_PRECOS];
    fala(partes.concat(pergunta), depoisDeFalar);
  }
  /* ---------- Depoimento em destaque: cópia exata do cartão do bloco de depoimentos da página (mesmo fundo, foto, estrelas,
     título e texto), com a etiqueta de destaque. O cartão escolhido é o do texto de CHAT_DEPOIMENTO_CORPO. ---------- */
  var depoimentoMostrado = false;
  /* v81: página sem bloco de depoimentos (nenhum depoimento real do produto): o chat nunca mostra depoimento */
  function temDepoimento(){ return !!modelo.content.querySelector('[data-r="depoimento"] p'); }
  function limpa(x){ return (x || "").replace(/\s+/g, " ").trim(); }
  function cartaoDepoimento(){
    var ref = modelo.content.querySelector('[data-r="depoimento"] p');
    if (!ref) return null;
    var alvo = limpa(ref.textContent), achado = null;
    /* Fábrica de review: #customer-reviews .review-card com o texto em .review-text. Mantém também o formato da demo (#depoimentos .depoimento blockquote). */
    document.querySelectorAll("#customer-reviews .review-card, #depoimentos .depoimento").forEach(function(a){ var q = a.querySelector(".review-text, blockquote"); if (!achado && q && limpa(q.textContent) === alvo) achado = a; });
    if (!achado) return null;
    var caixa = document.createElement("div"); caixa.className = "chat-destaque";
    var tag = document.createElement("span"); tag.className = "chat-destaque-tag"; tag.textContent = "★ Featured customer review"; caixa.appendChild(tag);
    caixa.appendChild(achado.cloneNode(true));
    var leg = document.createElement("span"); leg.className = "chat-destaque-legenda"; leg.textContent = "Also highlighted in the Customer Reviews section of this page"; caixa.appendChild(leg);
    return caixa;
  }
  function partesDepoimento(){
    var c = cartaoDepoimento(), primeira = !depoimentoMostrado;
    depoimentoMostrado = true;
    if (!c) return ["<p>Here's what one customer shared on the official website:</p>"].concat(baloes(txt("depoimento")), baloes(txt("depoimento-uso")));
    return ["<p>" + (primeira ? "I'd like to highlight one of the customer reviews featured on this page, because it shows " + esc(produto) + " in real life 👇"
                               : "Take another look at the review I highlighted, one of those featured on this page 👇") + "</p>", c].concat(baloes(txt("depoimento-uso")));
  }
  /* ---------- Respostas por tema (as mesmas no meio do roteiro, na recusa e nas perguntas livres) ---------- */
  function conteudo(ch){
    if (ch === "caro") return baloes(txt("preco-dia")).concat(baloes(txt("garantia-curta")));
    if (ch === "funciona") return temDepoimento() ? partesDepoimento() : baloes(txt("resultados"));
    if (ch === "seguranca") return baloes(txt("seguranca")).concat(["<p>If you take medication or have a health condition, please talk to your doctor before using it.</p>"]);
    return baloes(txt(ch));
  }
  /* Objeção ou pergunta no meio do roteiro: responde e volta para a pergunta da vez */
  var TEMA_DA_PERGUNTA = { ingredientes: ["ingredientes"], resultados: ["funciona"], uso: ["uso"], oferta: ["preco", "onde"] };
  function objecaoNoMeio(t){
    if (!pergunta.length || ["tempo", "dor", "tentou", "ingredientes", "resultados", "uso", "oferta"].indexOf(passo) === -1) return "";
    var ch = tema(t);
    if (ch === "nao-sei") return "";
    if (ch === "seguranca") return ch;
    if (passo === "tempo" || passo === "dor") return (ch === "caro" || /\?/.test(t)) ? ch : "";
    if (ehSim(t) || ehNao(t)) return "";
    if ((TEMA_DA_PERGUNTA[passo] || []).indexOf(ch) !== -1) return "";
    return ch;
  }
  function responderNoMeio(ch){
    fala(conteudo(ch).concat(["<p>Now, back to where we were, " + esc(nome) + ":</p>"], pergunta), focar);
  }
  /* ---------- Quando a pessoa some ou fecha (a partir da pergunta da oferta): um lembrete por silêncio ---------- */
  function depoisDeFalar(){ focar(); if (chegouOferta && !compraAvisada) vigiarSumico(); }
  function chamarDeVolta(){
    if (ofertaMostrada && passo !== "objecao" && passo !== "ver-precos") return ["<p>Still there, " + esc(nome) + "? If you have any question about the packages, I'm here 😊</p>"];
    passo = "ver-precos"; pergunta = [VER_PRECOS];
    return ["<p>Still there, " + esc(nome) + "? Whenever you're ready, I can show you the options 😊</p>", VER_PRECOS];
  }
  function vigiarSumico(){
    if (timerSumiu) clearTimeout(timerSumiu);
    timerSumiu = setTimeout(function(){
      timerSumiu = null;
      if (ocupado || pendente || compraAvisada) return;
      pendente = true;
      fala(chamarDeVolta());
    }, 40000);
  }
  function mostrarSelo(){
    if (!selo) return;
    var n = Math.max(naoLidas, 1);
    selo.textContent = n > 99 ? "99+" : String(n);
    selo.setAttribute("aria-label", n + (n === 1 ? " new message" : " new messages"));
    selo.hidden = false;
  }
  function esconderSelo(){ naoLidas = 0; if (selo) selo.hidden = true; }
  /* ---------- Perguntas livres ---------- */
  function responder(ch){
    var partes = conteudo(ch);
    if ((ch === "preco" || ch === "onde") && oferta) { partes.push("#divisor"); partes.push(cartoes(null)); partes = partes.concat(baloes(txt("preco-dia"))); ofertaMostrada = true; }
    partes.push("<p>Anything else I can help you with, " + esc(nome) + "?</p>");
    /* Depois da pergunta da oferta, cada resposta volta a contar os 40 s do lembrete */
    fala(partes, depoisDeFalar);
  }
  function tema(t){
    t = t.toLowerCase();
    if (/medic|drug|prescri|pill|metformin|ozempic|glp|diabet|insulin|thyroid|heart|pregnan|nursing|breastfeed|blood pressure|condition|doctor|allerg|side effect|safe|\b(?:take|use) it with (?!food|water|meals?|coffee|or without)/.test(t)) return "seguranca";
    if (/expensive|too much|afford|pricey|cheaper|can't pay|cannot pay|budget|so much money|a lot of money/.test(t)) return "caro";
    if (/price|cost|how much|\$|package|bottle|discount|deal|kit/.test(t)) return "preco";
    if (/refund|guarantee|money back|money-back|return/.test(t)) return "garantia";
    if (/where|buy|order|amazon|ebay|walmart|store|official/.test(t)) return "onde";
    if (/ingredient|contain|formula|label|calorie|dose/.test(t)) return "ingredientes";
    if (/really work|does it work|work for me|it works|legit|scam|real\b|effective|result|reviews?|testimonial/.test(t)) return "funciona";
    if (/take|dosage|how many|when|morning|use it|daily/.test(t)) return "uso";
    return "nao-sei";
  }
  /* ---------- Clique em "Buy Now" dentro do chat ---------- */
  lista.addEventListener("click", function(e){
    var a = e.target.closest && e.target.closest(".chat-cartoes a");
    if (!a || compraAvisada) return;
    compraAvisada = true; if (timerSumiu) { clearTimeout(timerSumiu); timerSumiu = null; }
    setTimeout(function(){ fala(["<p>Great choice, " + esc(nome) + "! 🎉 You're being taken to the official secure checkout. If you have any question, I'm still here.</p>"]); }, 400);
  });
  /* ---------- Sons (gerados no navegador, nenhum arquivo externo) ----------
     Abertura: "plim" de duas notas. Mensagem recebida: dois toques curtos e suaves, no estilo dos apps de mensagem.
     Regra dos navegadores (Chrome, Safari, Firefox, Edge): nenhum som toca antes do primeiro gesto da pessoa na página
     (clique, toque ou tecla; rolar a página não conta). Por isso o áudio é liberado no primeiro gesto (inclusive o
     Accept/Decline do banner) e, a partir daí, toca na abertura automática, na abertura por clique e em cada mensagem. */
  var audio = null;
  function liberarAudio(){
    try {
      var AC = window.AudioContext || window.webkitAudioContext; if (!AC) return;
      if (!audio) audio = new AC();
      if (audio.state !== "running") audio.resume();
      /* iPhone/iPad: tocar um som mudo dentro do gesto destrava o áudio de vez */
      var buf = audio.createBuffer(1, 1, 22050), src = audio.createBufferSource(); src.buffer = buf; src.connect(audio.destination); src.start(0);
    } catch(e){}
  }
  ["pointerdown","pointerup","touchstart","touchend","mousedown","click","keydown"].forEach(function(ev){ document.addEventListener(ev, liberarAudio, { capture: true, passive: true }); });
  function nota(t, freq, fim, inicio, dur, vol){
    var o = audio.createOscillator(), g = audio.createGain();
    o.type = "sine"; o.frequency.setValueAtTime(freq, t + inicio);
    if (fim) o.frequency.exponentialRampToValueAtTime(fim, t + inicio + dur);
    g.gain.setValueAtTime(0.0001, t + inicio); g.gain.exponentialRampToValueAtTime(vol, t + inicio + 0.008); g.gain.exponentialRampToValueAtTime(0.0001, t + inicio + dur);
    o.connect(g); g.connect(audio.destination); o.start(t + inicio); o.stop(t + inicio + dur + 0.02);
  }
  /* Toca já se o áudio estiver liberado; se ele estiver só "acordando" (resume em andamento), toca assim que acordar */
  function quandoAudio(fn){
    try {
      if (!audio) return false;
      if (audio.state === "running") { fn(audio.currentTime); return true; }
      if (navigator.userActivation && !navigator.userActivation.hasBeenActive) return false;
      audio.resume().then(function(){ if (audio.state === "running") fn(audio.currentTime); }).catch(function(){});
    } catch(e){}
    return false;
  }
  function tocarSom(){
    quandoAudio(function(t){ nota(t, 880, 0, 0, 0.22, 0.18); nota(t, 1318.5, 0, 0.11, 0.22, 0.18); window.__chatSom = (window.__chatSom || 0) + 1; });
  }
  function tocarMsg(){
    quandoAudio(function(t){ nota(t, 1250, 900, 0, 0.07, 0.14); nota(t, 1650, 1150, 0.09, 0.08, 0.12); window.__chatMsgSom = (window.__chatMsgSom || 0) + 1; });
  }
  /* ---------- Abrir e fechar ---------- */
  /* REGRA FIXA v42: "Specialist in [nicho]" no topo do chat sempre numa linha só; se não couber, a letra diminui (até 10px) */
  function caberNicho(){
    var st = jan.querySelector(".chat-topo .status"); if (!st) return;
    var pil = jan.querySelector(".chat-topo .pilula");
    st.style.fontSize = ""; if (pil) pil.style.display = "";
    if (st.scrollWidth > st.clientWidth + 0.5 && pil) pil.style.display = "none"; /* primeiro tira a pílula "Online" (a bolinha verde continua) */
    var av = jan.querySelector(".chat-topo .chat-avatar"); if (av) av.style.display = "";
    function reduzir(min){ var t = 13; st.style.fontSize = ""; while (st.scrollWidth > st.clientWidth + 0.5 && t > min){ t -= 0.5; st.style.fontSize = t + "px"; } }
    reduzir(11);
    if (st.scrollWidth > st.clientWidth + 0.5 && av){ av.style.display = "none"; reduzir(10); } /* telas muito estreitas: a foto sai do topo, o nicho continua inteiro */
  }
  /* REGRA FIXA v42: na pílula do celular o nicho também fica numa linha só; se não couber, a letra diminui e, em tela muito estreita, a foto sai */
  function caberPilula(){
    var r = lanc.querySelector(".rotulo-cel"), av = lanc.querySelector(".chat-avatar"); if (!r) return;
    r.style.fontSize = ""; if (av) av.style.display = "";
    if (getComputedStyle(r).display === "none") return;
    function cabe(){ var q = r.getBoundingClientRect(), l = lanc.getBoundingClientRect(); return r.scrollWidth <= r.clientWidth + 0.5 && q.right <= l.right - 8 && l.left >= 0; }
    function reduzir(min){ var t = 13; r.style.fontSize = ""; while (!cabe() && t > min){ t -= 0.5; r.style.fontSize = t + "px"; } }
    reduzir(11);
    if (!cabe() && av){ av.style.display = "none"; reduzir(10); }
  }
  caberPilula();
  /* As fontes vêm da página (Poppins 700 chega depois): mede de novo quando terminam de carregar */
  try { document.fonts.ready.then(function(){ caberPilula(); if (!jan.hidden) caberNicho(); }); } catch(e){}
  window.addEventListener("resize", function(){ caberPilula(); if (!jan.hidden) caberNicho(); });
  function abrir(auto){
    if (jan.hidden) { if (!auto) liberarAudio(); tocarSom(); }
    esconderBalao(); lanc.classList.remove("aguardando"); jan.hidden = false; caberNicho(); lanc.classList.add("aberto"); document.documentElement.classList.add("chat-aberto"); esconderSelo();
    if (!iniciou) iniciarConversa(!auto);
    else if (!auto) { campo.focus(); rolar(); }
  }
  /* Começa a conversa (as duas mensagens de boas-vindas), com o som de mensagem recebida em cada uma. */
  function iniciarConversa(focarNoFim){
    iniciou = true;
    var s = document.createElement("p"); s.className = "chat-sessao"; s.textContent = "Starting your session…"; lista.appendChild(s);
    setTimeout(function(){ s.textContent = (/^Dr\.\s/.test(pessoa) ? pessoa : pessoa.split(" ")[0]) + " joined the chat"; /* v60: "Dr. Emily Parker joined the chat" (nunca "Dr. joined") */ fala(["<p>Hi there, welcome! 👋 I'm here to answer any questions about " + esc(produto) + ".</p>", "<p>To start your session, what is your name? 😊</p>"], function(){ if (focarNoFim && !jan.hidden) campo.focus(); }); }, reduz ? 200 : 1300);
  }

  /* Celular: com o teclado aberto, a janela sobe para ficar acima dele (altura visível medida pelo visualViewport) */
  if (window.visualViewport) {
    var vv = window.visualViewport;
    var ajustarTeclado = function(){
      var teclado = Math.max(0, window.innerHeight - vv.height - vv.offsetTop);
      jan.style.setProperty("--teclado", Math.round(teclado) + "px");
      jan.style.setProperty("--altura-visivel", Math.round(vv.height) + "px");
    };
    vv.addEventListener("resize", ajustarTeclado); vv.addEventListener("scroll", ajustarTeclado); ajustarTeclado();
  }
  function fecharChat(){
    jan.hidden = true; lanc.classList.remove("aberto"); document.documentElement.classList.remove("chat-aberto"); lanc.focus();
    setTimeout(mostrarBalao, 1200);
    /* Fechou depois da pergunta da oferta (viu os pacotes ou recusou): alguns segundos depois chega uma mensagem (som + selo) */
    if (chegouOferta && !pendente && !compraAvisada) {
      pendente = true; if (timerSumiu) { clearTimeout(timerSumiu); timerSumiu = null; }
      (function esperar(){
        if (ocupado) { setTimeout(esperar, 500); return; }
        setTimeout(function(){
          if (ocupado) { esperar(); return; }
          if (!jan.hidden) return;
          if (ofertaMostrada && passo !== "objecao" && passo !== "ver-precos") fala(["<p>Did you have any questions about the packages, " + esc(nome) + "? I'm right here if you need me 😊</p>"]);
          else { passo = "ver-precos"; pergunta = [VER_PRECOS]; fala(["<p>Did you have any questions, " + esc(nome) + "? Whenever you're ready, I can show you the options 😊</p>", VER_PRECOS]); }
        }, reduz ? 300 : 2500);
      })();
    }
  }
  lanc.addEventListener("click", function(){ marcar(); abrir(false); });
  /* Versão Google Ads da fábrica: um script manda qualquer clique na página para o link de afiliado (document click).
     Clique dentro do chat (botão, campo, Enviar, fechar) não sobe até o document, então a conversa funciona.
     Os links "Buy Now" dos cartões continuam abrindo o checkout normalmente. */
  [lanc, jan].forEach(function(el){ el.addEventListener("click", function(e){ e.stopPropagation(); }); });
  fechar.addEventListener("click", fecharChat);
  document.addEventListener("keydown", function(e){ if (e.key === "Escape" && !jan.hidden) fecharChat(); });
  form.addEventListener("submit", function(e){
    e.preventDefault();
    var t = campo.value.replace(/\s+/g, " ").trim();
    if (!t || ocupado) return;
    if (timerSumiu) { clearTimeout(timerSumiu); timerSumiu = null; }
    pendente = false; /* ela respondeu: o próximo silêncio pode ter um novo lembrete */
    campo.value = ""; bolha(t, true);
    if (passo === "nome") { nome = t.split(" ")[0].slice(0, 30); campo.placeholder = "Type a message..."; ROTEIRO.tempo(); return; }
    var meio = objecaoNoMeio(t);
    if (meio) { responderNoMeio(meio); return; }
    if (passo === "objecao") { tratarObjecao(t); return; }
    if (passo === "ver-precos") {
      if (ehNao(t)) { passo = "livre"; pergunta = []; fala(["<p>No problem, " + esc(nome) + ". I'm right here if you have any other question 😊</p>"], depoisDeFalar); return; }
      if (!ehSim(t) && tema(t) !== "nao-sei" && tema(t) !== "preco" && tema(t) !== "onde") { tratarObjecao(t); return; }
      mostrarOferta(false); return;
    }
    if (passo === "tempo") { resp.tempo = t; return ROTEIRO.dor(); }
    if (passo === "dor") { resp.dor = t; return ROTEIRO.tentou(); }
    if (passo === "tentou") { resp.tentou = !ehNao(t); return ROTEIRO.como(ehNao(t)); }
    if (passo === "ingredientes") return ROTEIRO.ingredientes(ehNao(t));
    if (passo === "resultados") return ROTEIRO.resultados(ehNao(t));
    if (passo === "uso") return ROTEIRO.uso(ehNao(t));
    if (passo === "oferta") return ROTEIRO.oferta(ehNao(t));
    /* "Não" depois de ver os pacotes: na primeira vez pergunta o que está segurando; depois, só fica à disposição */
    if (chegouOferta && ehNao(t) && tema(t) === "nao-sei") {
      if (ofertaMostrada && !perguntouObjecao) { recusou(); return; }
      fala(["<p>No problem, " + esc(nome) + ". I'm right here if you have any other question 😊</p>"], depoisDeFalar); return;
    }
    responder(tema(t));
  });
  /* ---------- Abre sozinho 5 s depois que a página fica livre (com o banner de cookies na tela, conta a partir do Accept/Decline). Uma vez por visita. ---------- */
  var CHAVE_CHAT = "lp_chat_auto_v1", timerAuto = null;
  function jaAbriu(){ try { return sessionStorage.getItem(CHAVE_CHAT) === "1"; } catch(e){ return false; } }
  function marcar(){ try { sessionStorage.setItem(CHAVE_CHAT, "1"); } catch(e){} }
  /* REGRA FIXA v70 (pedido do Amorim, 2026-10-12): no CELULAR o chat NÃO abre sozinho (botão e balão continuam; abre pelo toque).
     No tablet e no computador continua abrindo sozinho 4 s depois que o botão aparece. Celular = o menor lado da tela abaixo de
     600px (vale em pé e deitado; tablets começam em 600px; não depende do tamanho da janela do navegador). */
  function telaDeCelular(){ try { return Math.min(screen.width, screen.height) < 600; } catch(e){ return false; } }
  function agendarAuto(){
    if (timerAuto || iniciou || jaAbriu()) return; /* 2026-10-16 (pedido do usuário): abre sozinho também no celular */
    timerAuto = setTimeout(function(){
      timerAuto = null;
      if (iniciou || jaAbriu() || (banner && !banner.hidden)) return;
      if (document.documentElement.classList.contains("popup-aberto")) { agendarAuto(); return; } /* v66: o chat espera o pop-up fechar */
      marcar(); abrir(true); /* abre sozinho 4 s depois que o botão aparece (7 s ao todo), em todo aparelho */
    }, 4000);
  }
  /* ---------- Balão em cima do botão com o chat fechado, em todo aparelho (REGRA FIXA v38) ----------
     Antes da conversa: "Hi! Can I help you? 😊". Depois que ela começou: a última mensagem da especialista (a que chegou com o
     chat fechado aparece na hora). Fica 7 s na tela e volta a cada 20 s enquanto o chat estiver fechado. */
  var balao = document.getElementById("chat-balao"), timerBalao = null;
  function textoBalao(){
    if (!iniciou) return "Hi! Can I help you? 😊";
    var bs = lista.querySelectorAll(".chat-msg.ela:not(.digitando):not(.cartoes):not(.destaque) .bolha");
    if (!bs.length) return "Hi! Can I help you? 😊";
    var b = bs[bs.length - 1].cloneNode(true), h = b.querySelector(".hora"); if (h) h.remove();
    var x = b.textContent.replace(/\s+/g, " ").trim();
    if (lista.lastElementChild && lista.lastElementChild.classList.contains("cartoes")) x = lista.lastElementChild.querySelector(".chat-cartao") ? "Here are the options I picked for you, " + nome + " 👇" : "Here's the official website link, " + nome + " 👇";
    return x.length > 90 ? x.slice(0, 87).replace(/\s+\S*$/, "") + "…" : x;
  }
  function mostrarBalao(){
    if (!balao || !jan.hidden || lanc.classList.contains("escondido") || lanc.classList.contains("aguardando")) return;
    balao.textContent = textoBalao(); balao.classList.add("visivel");
    if (timerBalao) clearTimeout(timerBalao);
    timerBalao = setTimeout(function(){ balao.classList.remove("visivel"); }, 7000);
  }
  function esconderBalao(){ if (balao) balao.classList.remove("visivel"); if (timerBalao) { clearTimeout(timerBalao); timerBalao = null; } }
  setInterval(mostrarBalao, 20000);
  /* REGRA FIXA v39 — Botão do chat: aparece 3 s depois que a página fica livre (com o banner de cookies, conta a partir do Accept/Decline),
     subindo de baixo para cima; logo depois chega o balão "Hi! Can I help you? 😊"; o chat abre sozinho 4 s depois que o botão aparece
     (7 s ao todo) no tablet e no computador; no celular, só pelo toque (v70). */
  var timerSurgir = null;
  function agendarSurgir(){
    if (timerSurgir || !lanc.classList.contains("aguardando")) return;
    timerSurgir = setTimeout(function(){
      timerSurgir = null;
      if (banner && !banner.hidden) return;
      lanc.classList.remove("aguardando"); lanc.classList.add("surgiu");
      setTimeout(mostrarBalao, reduz ? 100 : 700);
      agendarAuto();
    }, 3000);
  }
  function conferirBanner(){
    var visivel = !!(banner && !banner.hidden);
    lanc.classList.toggle("escondido", visivel);
    if (visivel) { esconderBalao(); if (timerAuto) { clearTimeout(timerAuto); timerAuto = null; } }
    else if (lanc.classList.contains("aguardando")) agendarSurgir(); /* o botão aparece em 3 s e o chat abre 4 s depois */
    else agendarAuto();
  }
  conferirBanner();
  if (banner && window.MutationObserver) new MutationObserver(conferirBanner).observe(banner, { attributes: true, attributeFilter: ["hidden"] });
});
