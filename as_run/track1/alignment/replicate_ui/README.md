# Visor de replicacion (MVA)

1. Instala Python 3 (sin dependencias extra).
2. Desde esta carpeta: python3 replicate_ui.py
3. Abre http://127.0.0.1:8765
4. Escribe la carpeta de datos (con los FASTQ y el VCF del reto) y la carpeta de trabajo.
5. Pulsa Ejecutar en cada paso, en orden. Cada paso muestra su proposito, el resultado esperado y su estado.

Los pasos de GPU tardan horas; los controles (datos, referencia, chr15, BUB1B) tardan segundos.
El visor solo ejecuta los pasos de steps.json y escucha en 127.0.0.1.
Los scripts que llama estan en ../scripts/ (ver REPRODUCE.md).
