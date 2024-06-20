function filterTable() {
    var input = document.getElementById("search-input").value.toLowerCase();
    var profesion = document.getElementById("profesion-select").value.toLowerCase();
    var tipoDireccion = document.getElementById("tipo-direccion-select").value.toLowerCase();
    var productoPrincipal = document.getElementById("producto-principal-select").value.toLowerCase();
    var tipoParroquia = document.getElementById("tipo-parroquia-select").value.toLowerCase();
    var rows = document.getElementsByTagName("tr");

    for (var i = 1; i < rows.length; i++) {
        var cells = rows[i].getElementsByTagName("td");
        var match = false;
        var profesionMatch = false;
        var tipoDireccionMatch = false;
        var productoPrincipalMatch = false;
        var tipoParroquiaMatch = false;

        for (var j = 0; j < cells.length; j++) {
            var cellValue = cells[j].textContent.toLowerCase();

            if (cellValue.includes(input)) {
                match = true;
            }

            if (cells[8].textContent.toLowerCase() === profesion || profesion === "") {
                profesionMatch = true;
            }

            if (cells[11].textContent.toLowerCase() === tipoDireccion || tipoDireccion === "") {
                tipoDireccionMatch = true;
            }

            if (cells[23].textContent.toLowerCase() === productoPrincipal || productoPrincipal === "") {
                productoPrincipalMatch = true;
            }

            if (cells[13].textContent.toLowerCase() === tipoParroquia || tipoParroquia === "") {
                tipoParroquiaMatch = true;
            }
        }

        if (match && profesionMatch && tipoDireccionMatch && productoPrincipalMatch && tipoParroquiaMatch) {
            rows[i].style.display = "";
        } else {
            rows[i].style.display = "none";
        }
    }
}

document.getElementById("search-input").addEventListener("input", filterTable);
document.getElementById("profesion-select").addEventListener("change", filterTable);
document.getElementById("tipo-direccion-select").addEventListener("change", filterTable);
document.getElementById("producto-principal-select").addEventListener("change", filterTable);
document.getElementById("tipo-parroquia-select").addEventListener("change", filterTable);