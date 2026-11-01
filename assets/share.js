/* Share buttons.
   Phones: the native share sheet, sending the day's or story's custom card image together with the link.
   Desktop: a small menu with WhatsApp, X, copy link and "Save share image". */
(function(){
  var pop=null, cache={};
  function close(){if(pop){pop.remove();pop=null}}
  function item(tag,label,href){var el=document.createElement(tag);el.textContent=label;el.setAttribute("role","menuitem");
    if(href){el.href=href;el.target="_blank";el.rel="noopener"}else{el.type="button"}return el}
  function getImage(src){
    if(!src)return Promise.resolve(null);
    if(!cache[src])cache[src]=fetch(src).then(function(r){if(!r.ok)throw 0;return r.blob()})
      .then(function(b){return new File([b],"the-daily-deploy-"+src.split("/").pop(),{type:"image/png"})})
      .catch(function(){delete cache[src];return null});
    return cache[src];
  }
  // Fetch the card as soon as someone points at or touches a button, so sharing feels instant.
  ["pointerover","touchstart","focusin"].forEach(function(t){document.addEventListener(t,function(e){
    var b=e.target.closest&&e.target.closest("[data-share]");if(b)getImage(b.getAttribute("data-img"))},{passive:true})});

  document.addEventListener("click",function(ev){
    var b=ev.target.closest("[data-share]");
    if(!b){if(pop&&!pop.contains(ev.target))close();return}
    ev.preventDefault();
    var url=b.getAttribute("data-url"),title=b.getAttribute("data-title"),img=b.getAttribute("data-img");
    var text=title+" | via @dailydeploybysaj";
    if(navigator.share){
      b.setAttribute("aria-busy","true");
      getImage(img).then(function(file){
        b.removeAttribute("aria-busy");
        var data={title:title,text:text+"\n"+url,url:url};
        if(file&&navigator.canShare&&navigator.canShare({files:[file]})){
          // Some apps drop the url field when an image is attached, so the link also rides in the text.
          return navigator.share({title:title,text:text+"\n"+url,files:[file]}).catch(function(e){
            if(e&&e.name==="AbortError")return;
            return navigator.share({title:title,text:text,url:url}).catch(function(){});
          });
        }
        return navigator.share({title:title,text:text,url:url}).catch(function(){});
      });
      return;
    }
    if(pop&&pop._for===b){close();return}
    close();
    var enc=encodeURIComponent;
    pop=document.createElement("div");pop.className="sharepop";pop.setAttribute("role","menu");pop._for=b;
    pop.appendChild(item("a","WhatsApp","https://wa.me/?text="+enc(text+" "+url)));
    pop.appendChild(item("a","X (Twitter)","https://twitter.com/intent/tweet?text="+enc(text)+"&url="+enc(url)));
    var copy=item("button","Copy link");
    copy.addEventListener("click",function(){
      var done=function(){copy.textContent="Link copied"};
      if(navigator.clipboard){navigator.clipboard.writeText(url).then(done,function(){window.prompt("Copy this link",url)})}else{window.prompt("Copy this link",url)}
    });
    pop.appendChild(copy);
    if(img){
      var save=item("a","Save share image",img);
      save.removeAttribute("target");save.setAttribute("download","the-daily-deploy-"+img.split("/").pop());
      pop.appendChild(save);
    }
    document.body.appendChild(pop);
    var r=b.getBoundingClientRect(),w=pop.offsetWidth;
    pop.style.top=(window.scrollY+r.bottom+6)+"px";
    pop.style.left=Math.max(8,Math.min(window.scrollX+r.right-w,window.scrollX+document.documentElement.clientWidth-w-8))+"px";
    pop.firstChild.focus();
  });
  document.addEventListener("keydown",function(e){if(e.key==="Escape")close()});
  window.addEventListener("resize",close);
})();
