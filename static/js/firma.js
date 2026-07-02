// Pad de firma sobre canvas. Guarda la imagen como dataURL en el input #firmaData.
(function () {
    var canvas = document.getElementById('firmaCanvas');
    if (!canvas) return;
    var ctx = canvas.getContext('2d');
    var dibujando = false;
    var hayFirma = false;
    var input = document.getElementById('firmaData');

    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.strokeStyle = '#111';

    function pos(e) {
        var rect = canvas.getBoundingClientRect();
        var scaleX = canvas.width / rect.width;
        var scaleY = canvas.height / rect.height;
        var clientX = e.touches ? e.touches[0].clientX : e.clientX;
        var clientY = e.touches ? e.touches[0].clientY : e.clientY;
        return { x: (clientX - rect.left) * scaleX, y: (clientY - rect.top) * scaleY };
    }

    function start(e) { dibujando = true; var p = pos(e); ctx.beginPath(); ctx.moveTo(p.x, p.y); e.preventDefault(); }
    function move(e) {
        if (!dibujando) return;
        var p = pos(e); ctx.lineTo(p.x, p.y); ctx.stroke(); hayFirma = true;
        guardar(); e.preventDefault();
    }
    function end() { dibujando = false; }

    function guardar() { if (input && hayFirma) input.value = canvas.toDataURL('image/png'); }

    canvas.addEventListener('mousedown', start);
    canvas.addEventListener('mousemove', move);
    canvas.addEventListener('mouseup', end);
    canvas.addEventListener('mouseout', end);
    canvas.addEventListener('touchstart', start);
    canvas.addEventListener('touchmove', move);
    canvas.addEventListener('touchend', end);

    var btn = document.getElementById('limpiarFirma');
    if (btn) btn.addEventListener('click', function () {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        hayFirma = false;
        if (input) input.value = '';
    });
})();
