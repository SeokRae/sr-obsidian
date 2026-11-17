// 배포 화면의 구성 윤곽을 위에서 아래 순서로 뽑는다. wireframe-verifier 가 javascript_tool 로 실행한다.
// 화면 문구(제목, 탭, 접이식 제목, 라벨, 버튼, 표 머리)만 담고, 표 칸과 숫자 같은 데이터 값은 담지 않는다.
// 결과는 90항목으로 자른다. 도구 출력이 약 1,500자에서 잘리므로 항목이 많으면 SLICE 를 바꿔 나눠 읽는다.
// innerWidth 가 1200 미만이면 모바일 배치라 대조하지 않는다(narrow: true 로 돌려준다).
await new Promise(r => setTimeout(r, 2500));
(() => {
  const SLICE = [0, 90];
  const root = document.querySelector('main') || document.body;
  const vis = e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  const out = [];
  root.querySelectorAll('h1,h2,h3,h4,summary,label,button,th,[role=tab],[role=alert]').forEach(e => {
    if (!vis(e)) return;
    let t = (e.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 50);
    if (e.tagName === 'SUMMARY') t += e.parentElement.open ? ' [open]' : ' [closed]';
    if (t) out.push(e.tagName.toLowerCase() + ':' + t);
  });
  return { u: location.pathname, iw: innerWidth, narrow: innerWidth < 1200, n: out.length, items: out.slice(...SLICE) };
})()
