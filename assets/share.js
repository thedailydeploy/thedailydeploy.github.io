/* Share buttons: native share sheet on phones, a small WhatsApp / X / copy-link menu elsewhere. */
(function(){
  var pop=null;
  function close(){if(pop){pop.remove();pop=null}}
  function item(tag,label,href){var el=document.createElement(tag);el.textContent=label;el.setAttribute("role","menuitem");
    if(href){el.href=href;el.target="_blank";el.rel="noopener"}else{el.type="button"}return el}
  document.addEventListener("click",function(ev){
    var b=ev.target.closest("[data-share]");
    if(!b){if(pop&&!pop.contains(ev.target))close();return}
    ev.preventDefault();
    var url=b.getAttribute("data-url"),title=b.getAttribute("data-title"),text=title+" | via @dailydeploybysaj";
    if(navigator.share){navigator.share({title:title,text:text,url:url}).catch(function(){});return}
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
    document.body.appendChild(pop);
    var r=b.getBoundingClientRect(),w=pop.offsetWidth;
    pop.style.top=(window.scrollY+r.bottom+6)+"px";
    pop.style.left=Math.max(8,Math.min(window.scrollX+r.right-w,window.scrollX+document.documentElement.clientWidth-w-8))+"px";
    pop.firstChild.focus();
  });
  document.addEventListener("keydown",function(e){if(e.key==="Escape")close()});
  window.addEventListener("resize",close);
})();
