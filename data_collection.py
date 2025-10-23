from heapq import merge
import json
from github import Github, Auth
from datetime import datetime
from collections import defaultdict
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "Spring-projects"
REPO_NAME = "spring-boot"

if not GITHUB_TOKEN:
    raise ValueError("Token GitHub não encontrado. Use: export GITHUB_TOKEN='seu_token_aqui'")

auth = Auth.Token(GITHUB_TOKEN)
g = Github(auth=auth)
repository = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")

interactions = {
    "comentario_em_issues": [],
    "fechamento_de_issues": [],
    "comentario_pull_request": [],
    "revisoes_pull_request": [],
    "merge_pull_request": []
}

users_set = set()

def coletar_comentario_issues():
    print("Iniciando coleta de comentários em issues...")
    issues_count = 0
    try:
        for issue in repository.get_issues(state='all'):
            if issues_count >= 1000:
                print("Limite de 1000 issues atingido, parando coleta de comentários em issues.")
                break
            
            issue_creator = issue.user.login
            users_set.add(issue_creator)

            comment_count = 0
            for comment in issue.get_comments():
                commenter = comment.user.login
                users_set.add(commenter)
                if commenter != issue_creator:
                    interactions["comentario_em_issues"].append({
                        "weight": 2,
                        "from": commenter,
                        "to": issue_creator,
                        "type": "comentario_issue"
                    })
                comment_count += 1

            print(f"Issue {issues_count+1}: Criador - {issue_creator}, Comentários - {comment_count}")
            issues_count += 1
    except Exception as e:
        print(f"Erro ao coletar issues: {e}")

    print(f"Issues processadas: {issues_count}")


def coletar_fechamento_issue():
    print("Iniciando coleta de fechamentos de issues...")
    closed_count = 0
    try:
        for issue in repository.get_issues(state='closed'):
            if closed_count >= 1000:
                print("Limite de 1000 issues fechadas atingido, parando coleta de fechamentos.")
                break
            
            if issue.closed_by and issue.user:
                closer = issue.closed_by.login
                opener = issue.user.login
                users_set.add(closer)
                users_set.add(opener)
                if closer != opener:
                    interactions["fechamento_de_issues"].append({
                        "from": closer,
                        "to": opener,
                        "type": "fechamento_de_issue"
                    })
                print(f"Issue fechada {closed_count+1}: aberta por {opener}, fechada por {closer}")
            else:
                print(f"Issue fechada {closed_count+1}: sem informações completas.")

            closed_count += 1
        
        print(f"{closed_count} issues fechadas processadas")
    except Exception as e:
        print(f"Erro ao coletar issues fechadas: {e}")


def coletar_pull_request():
    print("Iniciando coleta de Pull Requests...")
    pr_count = 0
    try:
        for pr in repository.get_pulls(state="all"):
            if pr_count >= 1000:
                print("Limite de 1000 pull requests atingido, parando coleta de PRs.")
                break

            pr_creator = pr.user.login
            users_set.add(pr_creator)

            pr_comment_count = 0
            for comment in pr.get_comments():
                commenter = comment.user.login
                users_set.add(commenter)
                if commenter != pr_creator:
                    interactions["comentario_pull_request"].append({
                        "weight": 2,
                        "from": commenter,
                        "to": pr_creator,
                        "type": "comentario em pull request"
                    })
                pr_comment_count += 1

            pr_review_count = 0
            for review in pr.get_reviews():
                reviewer = review.user.login
                users_set.add(reviewer)
                if reviewer != pr_creator:
                    interactions["revisoes_pull_request"].append({
                        "weight": 4,
                        "from": reviewer,
                        "to": pr_creator,
                        "type": "revisao de pull request"
                    })
                pr_review_count += 1
            
            merge_log = ""
            if pr.merged_by:
                merger = pr.merged_by.login
                users_set.add(merger)
                if merger != pr_creator:
                    interactions["merge_pull_request"].append({
                        "weight": 5,
                        "from": merger,
                        "to": pr_creator,
                        "type": "merge_pull_request"
                    })
                merge_log = f", merge por {merger}"
            else:
                merge_log = ", não mergeada"

            print(f"PR {pr_count+1}: Criador - {pr_creator}, Comentários - {pr_comment_count}, Revisões - {pr_review_count}{merge_log}")
            pr_count += 1
        print(f"{pr_count} pull requests processadas")
    except Exception as e:
        print(f"Erro ao coletar PRs: {e}")


coletar_comentario_issues()
coletar_fechamento_issue()
coletar_pull_request()

print("\n=== RESUMO ===")
print(f"Total de usuários: {len(users_set)}")
print(f"Comentários em issues: {len(interactions['comentario_em_issues'])}")
print(f"Fechamentos de issues: {len(interactions['fechamento_de_issues'])}")
print(f"Comentários em PRs: {len(interactions['comentario_pull_request'])}")
print(f"Revisões de PRs: {len(interactions['revisoes_pull_request'])}")
print(f"Merges de PRs: {len(interactions['merge_pull_request'])}")

output = {
    "repository": f"{REPO_OWNER}/{REPO_NAME}",
    "data_collection_date": datetime.now().isoformat(),
    "users": sorted(list(users_set)),
    "interactions": interactions
}

with open("dados_github.json", "w") as f:
    json.dump(output, f, indent=2)

print("\n✓ Dados salvos em 'dados_github.json'")
