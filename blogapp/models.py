from django.db import models
from django.contrib.auth.models import User


class Article(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    auteur = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='articles_ecrits')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titre


class Commentaire(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='commentaires')
    auteur = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='commentaires_ecrits')
    contenu = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date_creation']  # les plus anciens d'abord

    def __str__(self):
        apercu = self.contenu[:30] + '...' if len(self.contenu) > 30 else self.contenu
        return f'Commentaire par {self.auteur.username} sur "{self.article.titre}" : "{apercu}"'
