# FFT & Quantum FFT Implementation

Ce projet permet d’appliquer la transformée de Fourier rapide (FFT) sur des fichiers audio et des images, pour visualiser leur spectre de fréquences ou effectuer une compression.

## Fonctionnement mathématique

La FFT est un algorithme efficace qui décompose un signal (audio ou image) en ses différentes fréquences. 
$$
X_k = \sum_{n=0}^{N-1} x_n\, e^{-2i\pi n k / N}
$$

Pour retrouver le signal original :

$$
x_n = \frac{1}{N} \sum_{k=0}^{N-1} X_k \, e^{2i\pi n k / N}
$$

- Pour l’audio, on segmente le signal en fenêtres, calcule la FFT de chaque, puis affiche l’énergie de chaque fréquence au fil du temps. On obtient un **spectrogramme** : un graphique où l’axe des x représente le temps, l’axe des y la fréquence, et les couleurs l’amplitude
- Pour les images, l’application de la FFT en 2D révèle les structures spatiales : les basses fréquences correspondent aux formes globales, les hautes fréquences aux détails et au bruit. Il est possible de retirer les hautes fréquences pour compresser (réduire la taille ou le bruit) l’image.

## Utilisation

1. Téléverse un fichier audio (.wav ou .mp3)  
 - visualisation du spectrogramme via FFT.  
2. Téléverse une image (.jpg, .png)
 - compression : la FFT permet d’éliminer certaines fréquences pour réduire le bruit ou la taille.
