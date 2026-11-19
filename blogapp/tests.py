from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Article, Commentaire


class BlogTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user('alice', password='motdepasse-123')
        self.bob = User.objects.create_user('bob', password='motdepasse-123')
        self.article = Article.objects.create(
            titre='Article de test', contenu='Contenu', auteur=self.alice)

    def test_accueil_accessible_a_tous(self):
        r = self.client.get(reverse('blogapp:accueil'))
        self.assertContains(r, 'Article de test')

    def test_creation_exige_connexion(self):
        r = self.client.get(reverse('blogapp:creer_article'))
        self.assertEqual(r.status_code, 302)
        self.assertIn('/connexion/', r.url)

    def test_seul_l_auteur_peut_supprimer(self):
        self.client.login(username='bob', password='motdepasse-123')
        self.client.post(reverse('blogapp:supprimer_article', args=[self.article.pk]))
        self.assertTrue(Article.objects.filter(pk=self.article.pk).exists())

    def test_auteur_ne_peut_pas_commenter_son_article(self):
        self.client.login(username='alice', password='motdepasse-123')
        self.client.post(
            reverse('blogapp:ajouter_commentaire', args=[self.article.pk]),
            {'contenu': 'Mon propre commentaire'})
        self.assertEqual(Commentaire.objects.count(), 0)

    def test_autre_utilisateur_peut_commenter(self):
        self.client.login(username='bob', password='motdepasse-123')
        self.client.post(
            reverse('blogapp:ajouter_commentaire', args=[self.article.pk]),
            {'contenu': 'Bravo !'})
        self.assertEqual(Commentaire.objects.count(), 1)

    def test_profil(self):
        r = self.client.get(reverse('blogapp:profil_utilisateur', args=['alice']))
        self.assertContains(r, 'Article de test')
