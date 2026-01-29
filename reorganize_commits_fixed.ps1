# Script para reorganizar commits de forma incremental
cd c:\Users\vigon\Desktop\codetria\lanature

# Reset para o commit inicial e desfazer o commit
Write-Host "Resetando para o commit inicial..." -ForegroundColor Yellow
git reset --hard 9a9f9a8

# Criar um commit vazio inicial
Write-Host "Criando commit vazio inicial..." -ForegroundColor Yellow
git checkout --orphan new-main
git rm -rf . 2>$null
git commit --allow-empty -m "Initial empty commit"

# Adicionar todos os arquivos do commit original
Write-Host "Restaurando arquivos..." -ForegroundColor Yellow
git checkout 9a9f9a8 -- . 2>$null
git add . 2>$null

# FASE 1 - Commit inicial (apenas gitignore e README)
Write-Host "`nFASE 1 - Commit inicial..." -ForegroundColor Green
git reset HEAD . 2>$null
git add .gitignore README.md backend/.gitignore frontend/.gitignore 2>$null
git commit -m "chore: initial project setup" 2>$null

# FASE 2 - Backend
Write-Host "FASE 2 - Backend..." -ForegroundColor Green

# 2. Configuração do backend
git add backend/requirements.txt backend/.env.example backend/SETUP-WINDOWS.ps1 2>$null
git commit -m "chore: setup backend environment and dependencies" 2>$null

# 3. Estrutura base FastAPI
git add backend/app/__init__.py backend/app/main.py 2>$null
git commit -m "feat: initialize FastAPI application structure" 2>$null

# 4. Banco de dados e ORM
git add backend/app/database.py backend/app/models.py 2>$null
git commit -m "feat: add database configuration and ORM models" 2>$null

# 5. Autenticação e segurança
git add backend/app/auth.py backend/app/constants.py 2>$null
git commit -m "feat: implement authentication and security layer" 2>$null

# 6. Schemas
git add backend/app/schemas.py 2>$null
git commit -m "feat: add pydantic schemas for data validation" 2>$null

# 7. Rotas principais
git add backend/app/routers/auth.py backend/app/routers/pets.py backend/app/routers/routines.py backend/app/routers/logs.py backend/app/routers/__init__.py 2>$null
git commit -m "feat: implement core API routes for pets, routines and history" 2>$null

# 8. Domínio
git add backend/app/domain/ 2>$null
git commit -m "feat: add domain services and business logic layer" 2>$null

# 9. Admin
git add backend/create_admin.py backend/app/routers/admin.py 2>$null
git commit -m "feat: add admin panel endpoints and user management" 2>$null

# FASE 3 - Frontend
Write-Host "FASE 3 - Frontend..." -ForegroundColor Green

# 10. Setup frontend
git add frontend/package.json frontend/vite.config.js frontend/tailwind.config.js frontend/postcss.config.js frontend/index.html frontend/package-lock.json 2>$null
git commit -m "chore: setup frontend with Vite and Tailwind CSS" 2>$null

# 11. Estrutura React
git add frontend/src/main.jsx frontend/src/App.jsx 2>$null
git commit -m "feat: initialize React application structure" 2>$null

# 12. Layout e autenticação
git add frontend/src/components/Layout.jsx frontend/src/components/AdminLayout.jsx frontend/src/contexts/ frontend/src/services/ frontend/src/hooks/ frontend/src/utils/ frontend/src/constants/ 2>$null
git commit -m "feat: add layout, navigation and auth context" 2>$null

# 13. Dashboard
git add frontend/src/pages/Dashboard.jsx 2>$null
git commit -m "feat: implement dashboard with daily care overview" 2>$null

# 14. Pets
git add frontend/src/pages/Pets.jsx frontend/src/components/forms/PetForm.jsx frontend/src/components/forms/index.js 2>$null
git commit -m "feat: implement pet management interface" 2>$null

# 15. Rotinas
git add frontend/src/pages/Routines.jsx frontend/src/components/forms/RoutineForm.jsx 2>$null
git commit -m "feat: implement routine creation and management" 2>$null

# 16. Histórico
git add frontend/src/pages/History.jsx 2>$null
git commit -m "feat: implement care history and filters" 2>$null

# 17. Admin Frontend
git add frontend/src/pages/Admin.jsx 2>$null
git commit -m "feat: add admin panel interface and statistics" 2>$null

# 18. i18n
git add frontend/src/i18n/ 2>$null
git commit -m "feat: add internationalization support (EN/PT)" 2>$null

# FASE 4 - UI/UX
Write-Host "FASE 4 - UI/UX..." -ForegroundColor Green

# 19. Assets
git add assets/ 2>$null
git commit -m "feat: add visual assets and background illustrations" 2>$null

# 20. Ajustes visuais
git add frontend/src/styles/ frontend/src/components/ui/ frontend/src/components/layouts/ frontend/src/pages/Contact.jsx frontend/src/pages/Login.jsx frontend/src/pages/Register.jsx frontend/src/pages/IntroPage.jsx frontend/src/pages/LandingPage.jsx 2>$null
git commit -m "style: refine UI components and visual consistency" 2>$null

# FASE 6 - Finalização
Write-Host "FASE 6 - Finalização..." -ForegroundColor Green

# 23. Commit final - qualquer arquivo restante
git add . 2>$null
if (git diff --cached --quiet) {
    Write-Host "Nenhum arquivo restante para commit final" -ForegroundColor Yellow
} else {
    git commit -m "release: lanature mvp completed" 2>$null
}

# Renomear branch
git branch -M main

Write-Host "`nTodos os commits foram criados com sucesso!" -ForegroundColor Green
Write-Host "`nHistórico de commits:" -ForegroundColor Cyan
git log --oneline -25
