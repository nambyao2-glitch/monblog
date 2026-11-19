from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import ArticleForm, CommentaireForm
from .models import Article

ARTICLES_PAR_PAGE = 5


# ---------------------------------------------------------------------------
# Accueil (avec pagination)
# ---------------------------------------------------------------------------
def accueil_view(request):
    tous_les_articles = Article.objects.select_related('auteur').order_by('-date_creation')

    paginator = Paginator(tous_les_articles, ARTICLES_PAR_PAGE)
    page_numero = request.GET.get('page')
    try:
        articles_pages = paginator.page(page_numero)
    except PageNotAnInteger:
        articles_pages = paginator.page(1)
    except EmptyPage:
        articles_pages = paginator.page(paginator.num_pages)

    return render(request, 'blogapp/accueil.html',
                  {'articles_a_afficher': articles_pages})


# ---------------------------------------------------------------------------
# Authentification
# ---------------------------------------------------------------------------
def inscription_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('blogapp:accueil')
    else:
        form = UserCreationForm()
    return render(request, 'blogapp/inscription.html', {'form': form})


def connexion_view(request):
    # Page demandée avant la connexion (ex: ?next=/article/creer/)
    suivant = request.POST.get('next') or request.GET.get('next', '')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            # On ne redirige que vers notre propre site (sécurité)
            if suivant and url_has_allowed_host_and_scheme(
                    suivant, allowed_hosts={request.get_host()},
                    require_https=request.is_secure()):
                return redirect(suivant)
            return redirect('blogapp:accueil')
    else:
        form = AuthenticationForm()
    return render(request, 'blogapp/connexion.html', {'form': form, 'next': suivant})


def deconnexion_view(request):
    # La déconnexion modifie l'état : on la fait sur un POST (bouton dans la barre de nav).
    if request.method == 'POST':
        logout(request)
    return redirect('blogapp:accueil')


# ---------------------------------------------------------------------------
# Articles (CRUD)
# ---------------------------------------------------------------------------
@login_required
def creer_article_view(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            nouvel_article = form.save(commit=False)
            nouvel_article.auteur = request.user
            nouvel_article.save()
            return redirect('blogapp:detail_article', pk=nouvel_article.pk)
    else:
        form = ArticleForm()
    return render(request, 'blogapp/creer_modifier_article.html',
                  {'form': form, 'action': 'Créer'})


def detail_article_view(request, pk):
    article = get_object_or_404(Article.objects.select_related('auteur'), pk=pk)
    commentaires = article.commentaires.select_related('auteur')
    return render(request, 'blogapp/detail_article.html', {
        'article': article,
        'commentaires': commentaires,
        'commentaire_form': CommentaireForm(),
    })


@login_required
def modifier_article_view(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if article.auteur != request.user:
        return redirect('blogapp:detail_article', pk=article.pk)

    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect('blogapp:detail_article', pk=article.pk)
    else:
        form = ArticleForm(instance=article)
    return render(request, 'blogapp/creer_modifier_article.html',
                  {'form': form, 'action': 'Modifier', 'article': article})


@login_required
def supprimer_article_view(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if article.auteur != request.user:
        return redirect('blogapp:detail_article', pk=article.pk)

    if request.method == 'POST':
        article.delete()
        return redirect('blogapp:accueil')
    return render(request, 'blogapp/confirmer_suppression_article.html',
                  {'article': article})


# ---------------------------------------------------------------------------
# Commentaires
# ---------------------------------------------------------------------------
@login_required
def ajouter_commentaire_view(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)

    # Règle : l'auteur de l'article ne peut pas commenter son propre article
    if article.auteur == request.user:
        return redirect('blogapp:detail_article', pk=article.pk)

    if request.method == 'POST':
        form = CommentaireForm(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.article = article
            commentaire.auteur = request.user
            commentaire.save()
    return redirect('blogapp:detail_article', pk=article.pk)


# ---------------------------------------------------------------------------
# Profil utilisateur
# ---------------------------------------------------------------------------
def profil_utilisateur_view(request, username):
    utilisateur_profil = get_object_or_404(User, username=username)
    articles_utilisateur = Article.objects.filter(
        auteur=utilisateur_profil).order_by('-date_creation')
    return render(request, 'blogapp/profil_utilisateur.html', {
        'utilisateur_profil': utilisateur_profil,
        'articles_utilisateur': articles_utilisateur,
    })
