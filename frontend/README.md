# LaNature Frontend

Frontend da aplicação LaNature - Plataforma de gestão de cuidados para pets.

## 🎯 Decisões de UX

### Hierarquia Visual

**Princípio:** Uma ação primária por tela, ações secundárias claras, resto como links sutis.

**Implementação:**
- **Dashboard:** "New Task" é o CTA principal (card grande, gradiente verde, shadow forte)
- **Pets/Routines:** Botão "Add" é primário (verde, shadow, semibold)
- **Ações secundárias:** Links e botões ghost para navegação
- **Ações terciárias:** Texto simples ou botões outline

**Benefício:** Usuário sempre sabe qual é a ação mais importante.

### Onboarding Mínimo

**Estratégia:** Sem modais ou tutoriais chatos. Mensagens contextuais que guiam naturalmente.

**Implementação:**
- Quando não há pets: Card destacado com "Let's get started" + botão de ação
- Quando há pets mas não há rotinas: Mensagem "Nothing here yet" + botão para criar primeira tarefa
- Mensagens sempre orientadas a ação, não apenas informativas

**Benefício:** Usuário novo sabe exatamente o que fazer sem ser interrompido.

### Feedback Visual

**Sistema de Alerts:**
- Posicionamento fixo no topo (sempre visível)
- Ícones visuais por tipo (✓ ✕ ⚠ ℹ️)
- Cores contrastantes e bordas grossas
- Duração aumentada (5s para ações críticas)
- Animação slide-down ao aparecer

**Loading States:**
- Spinner animado em botões durante ações
- Skeletons para listas (em vez de apenas "Loading...")
- Opacidade reduzida durante loading

**Benefício:** Usuário sempre sabe o resultado de suas ações.

## 🌍 Decisões de i18n

### Arquitetura

**Estrutura:**
```
/i18n
  /en
    - en.json (traduções principais)
    - ux.json (UX copy refinado)
  /pt
    - pt.json
    - ux.json
  - index.js (sistema de i18n)
```

**Separação UX Copy:**
- `ux.json` contém textos refinados como produto (empty states, success messages, errors)
- `en.json/pt.json` contém traduções funcionais (labels, placeholders, etc.)

**Benefício:** UX copy pode ser refinado independentemente das traduções técnicas.

### Internacionalização vs Tradução

**Não apenas traduzir, mas adaptar:**

1. **Datas:** Usa `Intl.DateTimeFormat` com locale apropriado
   - EN: "January 15, 2024"
   - PT-BR: "15 de janeiro de 2024"

2. **Números:** Usa `Intl.NumberFormat` para formatação local
   - EN: "1,234.56"
   - PT-BR: "1.234,56"

3. **Pluralização:** Sistema automático com suporte a zero/one/other
   - `plural('history.record', 0)` → "No records"
   - `plural('history.record', 1)` → "record"
   - `plural('history.record', 5)` → "records"

4. **Fallbacks:** Sistema elegante que:
   - Tenta idioma atual
   - Fallback para inglês
   - Se não encontrar, retorna última chave formatada (não a key completa)
   - Log de warning para debug

**Benefício:** Produto verdadeiramente internacional, não apenas traduzido.

### Locale Mapping

```javascript
en → en-US
pt → pt-BR
```

Todas as formatações respeitam o locale apropriado automaticamente.

## 🎨 Sistema de Design

### Cores e Identidade Visual

**Dashboard Cards:**
- Quick Actions: Azul (secundária)
- Today's Care Tasks: Verde (primária)
- Registered Pets: Laranja (terciária)

**Prioridades em Routines:**
- Manhã (0-11h): Azul (alta prioridade)
- Tarde (12-17h): Amarelo (média prioridade)
- Noite (18-23h): Verde (baixa prioridade)

### Componentes Reutilizáveis

- `Card` - Container padrão
- `Button` - Com variantes (primary, secondary, danger, ghost, outline)
- `Input` - Com estados de erro
- `Select` - Com custom arrow
- `Alert` - Com ícones e cores por tipo
- `Modal` - Com animações suaves
- `Skeleton` - Para loading states
- `ListSkeleton` - Para listas em loading
- `EmptyState` - Para estados vazios
- `PageHeader` - Header padrão de páginas

## 🔧 Trade-offs

### Performance vs UX

**Escolha:** Skeletons em vez de apenas spinners
- **Trade-off:** Mais código, mas UX muito melhor
- **Decisão:** Vale a pena - percepção de velocidade aumenta

### Simplicidade vs Funcionalidade

**Escolha:** Sistema i18n customizado em vez de biblioteca pesada
- **Trade-off:** Menos features, mas mais controle e bundle menor
- **Decisão:** Para 2 idiomas, custom é suficiente e mais performático

### Feedback vs Poluição Visual

**Escolha:** Alerts fixos no topo por 5 segundos
- **Trade-off:** Podem bloquear conteúdo, mas garantem visibilidade
- **Decisão:** 5s é suficiente para ler sem ser intrusivo, usuário pode fechar

### Onboarding vs Interrupção

**Escolha:** Mensagens contextuais em vez de modais de tutorial
- **Trade-off:** Menos "guia", mas menos interrupção
- **Decisão:** Mensagens contextuais são suficientes e menos chatas

## 📦 Tecnologias

- **React 18** - Framework UI
- **React Router DOM** - Roteamento
- **Tailwind CSS** - Estilização
- **Vite** - Build tool
- **i18n Custom** - Internacionalização

## 🚀 Como Executar

```bash
cd frontend
npm install
npm run dev
```

## 📝 Estrutura de Pastas

```
src/
  components/
    ui/          # Componentes base reutilizáveis
    forms/       # Formulários
    layouts/     # Layouts e estruturas de página
  pages/         # Páginas da aplicação
  hooks/         # Custom hooks
  services/      # API calls
  i18n/          # Sistema de internacionalização
  styles/        # Estilos globais
  utils/         # Utilitários
  constants/     # Constantes
```

## 🎯 Próximos Passos

- [ ] Adicionar mais pluralizações (pet/pets, task/tasks)
- [ ] Implementar formatação de tempo relativo ("2 hours ago")
- [ ] Adicionar mais skeletons para diferentes contextos
- [ ] Melhorar acessibilidade (ARIA labels, keyboard navigation)
- [ ] Adicionar testes de componentes críticos
