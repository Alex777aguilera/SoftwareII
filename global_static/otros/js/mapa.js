var marker;
var coords={};

mapa = function()
{
navigator.geolocation.getCurrentPosition(
  function(position){
    coords = {
      lng: position.coords.longitude,
      lat: position.coords.latitude
    };
    setMapa(coords);
    document.getElementById("lat").value = coords.lat;
    document.getElementById("lng").value = coords.lng;

    document.getElementById("id_latitud").value = coords.lat;
    document.getElementById("id_longitud").value = coords.lng;
  },function(error){console.log(error);});
}
function setMapa(coords){
  var map = new google.maps.Map(document.getElementById("map"),
  {
    zoom: 18,
    center: new google.maps.LatLng(coords.lat,coords.lng)
  });

  var marker = new google.maps.Marker({
    map: map,
    draggable: true,
    animation: google.maps.Animation.DROP,
    position: new google.maps.LatLng(coords.lat,coords.lng),
  });

  marker.addListener('click',toggleBounce);
  marker.addListener('dragend',function(event){
    document.getElementById("lat").value = this.getPosition().lat();
    document.getElementById("lng").value = this.getPosition().lng();

    document.getElementById("id_latitud").value = this.getPosition().lat();
    document.getElementById("id_longitud").value = this.getPosition().lng();
  });
}

function toggleBounce(){
  if(marker.getAnimation() !== null){
    marker.setAnimation(null);
  }else{
    marker.setAnimation(google.maps.Animation.BOUNCE);
  }
}

$(document).ready(function(){
      $('#tabla_finca').DataTable();
    });


    $('#tabla_finca').DataTable({
        "language": {
            "sLengthMenu":     "Mostrar MENU registros",
            "sZeroRecords":    "No se encontraron resultados",
            "sEmptyTable":     "Ningún dato disponible en esta tabla =(",
            "sInfo":           "Mostrando registros del START al END de un total de TOTAL registros",
            "sInfoEmpty":      "Mostrando registros del 0 al 0 de un total de 0 registros",
            "sInfoFiltered":   "(filtrado de un total de MAX registros)",
            "sInfoPostFix":    "",
            "sSearch":         "Buscar:",
            "sUrl":            "",
            "sInfoThousands":  ",",
            "sLoadingRecords": "Cargando...",
            "oPaginate": {
                "sFirst":    "Primero",
                "sLast":     "Último",
                "sNext":     "Siguiente",
                 "sPrevious": "Anterior"
            }
        }
    });