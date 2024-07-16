let map;
let markers = [];
let selectedLocation = null;
let directionsService;
let directionsRenderer;
let clientes = djangoVariables.clientes;
let travelMode = 'DRIVING'; 
let tipoDireccion = 'trabajo';
let currentMarkerIndex = null;
let waypointClientIds = []; 
let infoWindow;
const customIcon = djangoVariables.customIcon;

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 15,
        center: { lat: -3.99820, lng: -79.20445 }
    });

    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({ suppressMarkers: true });
    directionsRenderer.setMap(map);

    map.addListener('click', function (event) {
        const ingresarUbicacionButton = document.getElementById('ingresar-ubicacion');
        if (ingresarUbicacionButton.classList.contains('btn-custom-selected')) {
            if (markers.length > 0) {
                markers[0].setMap(null);
                markers = [];
            }
            selectedLocation = { lat: event.latLng.lat(), lng: event.latLng.lng() };
            let marker = new google.maps.Marker({
                position: selectedLocation,
                map: map,
                label: {
                    text: "1",
                    color: "white",
                    fontSize: "18px",
                    fontWeight: "medium"
                },
                icon: {
                    url: customIcon,
                    scaledSize: new google.maps.Size(36, 36),
                }
            });
            marker.addListener('click', function () {
                showVisitaModal(0);
            });
            marker.set('cliente_id', null);
            markers.push(marker);

            ingresarUbicacionButton.classList.remove('btn-custom-selected');
            ingresarUbicacionButton.classList.add('btn-custom');
        }
    });

    filterClientes(tipoDireccion);
}

function enableLocationSelection() {
    selectedLocation = true;
    document.getElementById('ingresar-ubicacion').classList.remove('btn-custom');
    document.getElementById('ingresar-ubicacion').classList.add('btn-custom-selected');
}

function setTravelMode(mode) {
    travelMode = mode;
    document.getElementById('btn-driving').classList.remove('btn-custom-selected');
    document.getElementById('btn-walking').classList.remove('btn-custom-selected');
    document.getElementById('driving-icon').src = "{% static 'img/driving.png' %}";
    document.getElementById('walking-icon').src = "{% static 'img/walking.png' %}";

    if (mode === 'DRIVING') {
        document.getElementById('btn-driving').classList.add('btn-custom-selected');
        document.getElementById('driving-icon').src = "{% static 'img/driving_white.png' %}";
    } else {
        document.getElementById('btn-walking').classList.add('btn-custom-selected');
        document.getElementById('walking-icon').src = "{% static 'img/walking_white.png' %}";
    }
    traceRoute();
}

function setDireccionType(type) {
    tipoDireccion = type;
    document.getElementById('btn-trabajo').classList.remove('btn-custom-selected');
    document.getElementById('btn-domicilio').classList.remove('btn-custom-selected');

    if (type === 'trabajo') {
        document.getElementById('btn-trabajo').classList.add('btn-custom-selected');
    } else {
        document.getElementById('btn-domicilio').classList.add('btn-custom-selected');
    }

    filterClientes(type);
}

function filterClientes(type) {
    const tbody = document.getElementById('clientes-tbody');
    tbody.innerHTML = ''; 

    clientes.forEach(cliente => {
        if ((type === 'trabajo' && cliente.latitud_trabajo && cliente.longitud_trabajo) ||
            (type === 'domicilio' && cliente.latitud_domicilio && cliente.longitud_domicilio)) {
            const row = document.createElement('tr');
            row.innerHTML = `
                    <td><input class="form-check-input" type="checkbox" value="${cliente.id}" id="cliente${cliente.id}" onchange="handleClientSelection()"></td>
                    <td>${cliente.nombre_cliente}</td>
                    <td>${type === 'trabajo' ? 'Trabajo' : 'Domicilio'}</td>
                    <td>${cliente.producto_principal}</td>
                `;
            tbody.appendChild(row);
        }
    });
}

function handleClientSelection() {
    if (selectedLocation) {
        traceRoute();
    }
}

function traceRoute() {
    if (!selectedLocation) {
        return;
    }

    let selectedClients = Array.from(document.querySelectorAll('#clientes-select input[type="checkbox"]:checked')).map(input => input.value);
    if (selectedClients.length === 0) {
        return;
    }

    let waypoints = [];
    waypointClientIds = []; 

    selectedClients.forEach(clientId => {
        let cliente = clientes.find(c => c.id == clientId);
        if (cliente) {
            let location;
            if (tipoDireccion === 'trabajo') {
                location = { lat: parseFloat(cliente.latitud_trabajo), lng: parseFloat(cliente.longitud_trabajo) };
            } else {
                location = { lat: parseFloat(cliente.latitud_domicilio), lng: parseFloat(cliente.longitud_domicilio) };
            }
            waypoints.push({ location: location });
            waypointClientIds.push(clientId);
        } else {
            console.error(`Cliente con ID ${clientId} no encontrado.`);
        }
    });

    const request = {
        origin: selectedLocation,
        destination: waypoints[waypoints.length - 1].location,
        waypoints: waypoints.slice(0, waypoints.length - 1),
        optimizeWaypoints: true,
        travelMode: travelMode
    };

    directionsService.route(request, function (result, status) {
        if (status == 'OK') {
            directionsRenderer.setDirections(result);

            markers.forEach(marker => marker.setMap(null));
            markers = [];

            let route = result.routes[0];
            let legs = route.legs;

            let marker = new google.maps.Marker({
                position: selectedLocation,
                map: map,
                label: {
                    text: "1",
                    color: "white",
                    fontSize: "18px",
                    fontWeight: "medium"
                },
                icon: {
                    url: customIcon,
                    scaledSize: new google.maps.Size(36, 36),
                }
            });
            marker.addListener('click', function () {
                showVisitaModal(0);
            });
            marker.set('cliente_id', null);
            markers.push(marker);

            for (let i = 0; i < legs.length; i++) {
                let marker = new google.maps.Marker({
                    position: legs[i].end_location,
                    map: map,
                    label: {
                        text: (i + 2).toString(),
                        color: "white",
                        fontSize: "18px",
                        fontWeight: "medium"
                    },
                    icon: {
                        url: customIcon,
                        scaledSize: new google.maps.Size(36, 36),
                    }
                });

                marker.addListener('click', (function (index) {
                    return function () {
                        showVisitaModal(index + 1);
                    };
                })(i));
                marker.set('cliente_id', waypointClientIds[i]);

                var infoWindow = new google.maps.InfoWindow({
                    content: `
                            `
                });
                marker.addListener('mouseover', function () {
                    let cliente = clientes.find(c => c.id == waypointClientIds[i]);
                    if (cliente) {
                        let contentString = `
                                <div class="custom-infowindow">
                                    <div class="titulo">${cliente.nombre_cliente}</div><br>
                                    <div class="etiqueta">Dirección: </div>Domicilio<br>
                                    <div class="etiqueta">Vivienda: </div>${cliente.tipo_vivienda_cliente}<br>
                                    <div class="etiqueta">Producto: </div>${cliente.producto_principal}<br>
                                    <div class="etiqueta">Profesión: </div>${cliente.profesion_cliente}<br>
                                </div>`;
                        infoWindow.setContent(contentString);
                        infoWindow.open(map, marker);
                    }
                });
                marker.addListener('mouseout', function () {
                    infoWindow.close();
                });
                markers.push(marker);
            }
        } else {
            alert('No se pudo calcular la ruta: ' + status);
            console.error('Error status: ', status);
            console.error('Result: ', result);
        }
    });
}

function showVisitaModal(markerIndex) {
    currentMarkerIndex = markerIndex;
    const modal = document.getElementById('visitaModal');

    let clienteId = markers[currentMarkerIndex].get('cliente_id');
    if (clienteId === null) {
        console.error(`Cliente ID no encontrado para el marcador ${currentMarkerIndex}`);
        return;
    }

    let cliente = clientes.find(c => c.id == clienteId);
    if (cliente) {
        document.getElementById('clienteNombre').textContent = `${cliente.nombre_cliente}`;
    } else {
        document.getElementById('clienteNombre').textContent = `No encontrado`;
    }

    modal.style.display = 'block';
}

function confirmVisita(exitosa) {
    const modal = document.getElementById('visitaModal');
    modal.style.display = 'none';

    let clienteId = markers[currentMarkerIndex].get('cliente_id');
    if (clienteId === null) {
        console.error(`Cliente ID no encontrado para el marcador ${currentMarkerIndex}`);
        return;
    }

    let visitadorId = document.getElementById('visitador-select').value;

    fetch(djangoVariables.registrarVisitaUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': djangoVariables.csrfToken
        },
        body: `cliente_id=${clienteId}&visitador_id=${visitadorId}&exitosa=${exitosa}`
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert(data.message);
                
                let marker = markers.find(marker => marker.get('cliente_id') === clienteId);

                if (marker) {
                    marker.setVisible(false);
                    
                    document.getElementById(`cliente${clienteId}`).checked = false;
                } else {
                    console.error(`Marcador con cliente_id ${clienteId} no encontrado.`);
                }
            } else {
                alert('No se pudo registrar la visita.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Ocurrió un error al registrar la visita.');
        });
}

window.onload = function () {
    initMap();
    filterClientes(tipoDireccion);
};
