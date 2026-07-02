// Utilidades generales del panel
document.addEventListener('DOMContentLoaded', function () {
    // Auto-cierre de alertas despues de 5 segundos
    setTimeout(function () {
        document.querySelectorAll('.alert-dismissible').forEach(function (el) {
            try {
                var alert = bootstrap.Alert.getOrCreateInstance(el);
                alert.close();
            } catch (e) { /* noop */ }
        });
    }, 5000);
});
