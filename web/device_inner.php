<?php
  $id = $_GET['id'];
  $control_php = file_get_contents("device_inner.html");
  $control_php = str_replace("{#ID}", $id, $control_php);
  echo $control_php;
?>