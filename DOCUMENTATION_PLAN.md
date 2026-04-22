# Documentatieplan voor alpha-python

## Toolkeuze

**MkDocs + Material for MkDocs + mkdocstrings → ReadTheDocs**

| Tool | Stijl | Sterkte |
|---|---|---|
| **Sphinx** | RST / MyST | De klassieker; meest krachtig maar complex |
| **MkDocs + Material** ✅ | Markdown | Modern, mooi, eenvoudig te onderhouden |
| **Pdoc** | Markdown | Alleen API reference, geen narrative docs |
| **Gitbook** | WYSIWYG | Goed voor niet-technische bijdragers |

Gekozen voor MkDocs + Material, de standaard bij moderne Python libraries als FastAPI, Pydantic en Typer.
ReadTheDocs ondersteunt MkDocs native. Markdown is eenvoudiger te onderhouden dan Sphinx's RST.

---

## Bestandsstructuur

```
docs/
├── requirements.txt            → MkDocs dependencies (voor ReadTheDocs)
├── index.md                    → Landing page
├── installation.md             → Installatie met alle extras
├── quickstart.md               → Quick start guide
├── changelog.md                → Inclusie vanuit CHANGELOG.md
├── concepts/
│   ├── index.md                → Architectuuroverzicht
│   ├── repository-pattern.md   → Repository + Unit of Work uitgelegd
│   └── dependency-injection.md → DI container + YAML config
├── guides/
│   ├── database.md             → SQLAlchemy integratie
│   ├── authentication.md       → OIDC/LDAP/Password auth
│   ├── api-generation.md       → CLI + OpenAPI codegen
│   └── flask-integration.md    → Flask/Connexion setup
└── reference/
    ├── index.md                → Overzicht publieke API
    ├── encoder.md              → JSONEncoder
    ├── domain-models.md        → Domain models (User, Group, Role, LifeCycleBase)
    ├── repositories.md         → Repository API
    ├── adapters.md             → Unit of Work
    ├── factories.md            → Factories
    ├── providers.md            → Auth providers
    ├── services.md             → Services
    ├── interfaces.md           → Interfaces/Protocols
    └── utils.md                → Utilities

mkdocs.yml                      → MkDocs configuratie
.readthedocs.yaml               → ReadTheDocs build configuratie
```

---

## Fasen

### Fase 1 — Tooling & Infrastructuur *(geïmplementeerd)*

- [x] `DOCUMENTATION_PLAN.md` aanmaken (dit bestand)
- [x] `mkdocs.yml` aanmaken — Material theme, mkdocstrings, navigatiestructuur
- [x] `.readthedocs.yaml` aanmaken — ReadTheDocs build config
- [x] `docs/requirements.txt` aanmaken — mkdocs-material + mkdocstrings
- [x] `docs/index.md` aanmaken — landing page
- [x] Alle stub-pagina's aanmaken (zodat navigatie klopt bij eerste build)
- [x] `docs/reference/*.md` aanmaken — mkdocstrings directives
- [x] `pyproject.toml` updaten — `[dependency-groups] docs` toevoegen
- [x] `README.md` updaten — documentatielink toevoegen

**Resultaat:** `mkdocs build` en `mkdocs serve` werken; ReadTheDocs build mogelijk.

---

### Fase 2 — API Reference *(uitwerken)*

- [ ] Docstrings in publieke API reviewen (alle ~70 exports in `src/alpha/__init__.py`)
- [ ] Ontbrekende of incomplete docstrings aanvullen (Google-style)
- [ ] Verificatie dat alle reference-pagina's correct renderen via `mkdocs build --strict`
- [ ] Controleer dat optionele dependencies (flask, ldap etc.) geen import-fouten geven

**Scope:**
- `alpha.encoder` → `JSONEncoder`
- `alpha.domain.models.*` → `BaseDomainModel`, `DomainModel`, `LifeCycleBase`, `User`, `Group`
- `alpha.repositories.*` → `SqlAlchemyRepository`, `RestApiRepository`
- `alpha.adapters.*` → `SqlAlchemyUnitOfWork`, `RestApiUnitOfWork`
- `alpha.factories.*` → `JWTFactory`, `ModelClassFactory`, `LoggingHandlerFactory`, type factories
- `alpha.providers.*` → `OIDCProvider`, `KeyCloakProvider`, `LDAPProvider`, `ADProvider`
- `alpha.services.*` → `AuthenticationService`, `UserLifecycleManagement`
- `alpha.interfaces.*` → alle abstracte interfaces/protocols
- `alpha.utils.*` → `LoggingConfigurator`, `GunicornLogger`, `Headers`
- `alpha.infra.models.*` → `SearchFilter`, `Operator`, `And`, `Or`, `OrderBy`, `JsonPatch`

---

### Fase 3 — Installatie & Quickstart *(uitwerken)*

- [ ] `docs/installation.md` uitschrijven — alle extras met uitleg wanneer je ze nodig hebt
  - Pip, Poetry en uv voorbeelden
  - Tabel met extras: `flask`, `postgresql`, `mysql`, `ldap`, `api-generator`
- [ ] `docs/quickstart.md` uitschrijven — end-to-end minimaal werkend voorbeeld
  - Bijv. SQLAlchemy + Repository + Unit of Work
  - Of: Flask API met OIDC-authenticatie

---

### Fase 4 — Conceptuele Docs *(uitwerken)*

- [ ] `docs/concepts/index.md` — architectuuroverzicht (lagen, patterns, hoe alles samenhangt)
- [ ] `docs/concepts/repository-pattern.md` — Repository + Unit of Work patroon uitgelegd
  - Wanneer gebruik je welk pattern?
  - Vergelijking `SqlAlchemyUnitOfWork` vs `RestApiUnitOfWork`
- [ ] `docs/concepts/dependency-injection.md` — DI container + YAML config uitgelegd

---

### Fase 5 — How-to Guides *(uitwerken)*

- [ ] `docs/guides/database.md` — `SqlAlchemyDatabase`, `SqlAlchemyRepository`, UoW met PostgreSQL/MySQL
- [ ] `docs/guides/authentication.md` — OIDC/KeyCloak setup, LDAP/AD, password auth met Argon2
- [ ] `docs/guides/api-generation.md` — `alpha` CLI commando's, OpenAPI code generatie workflow
- [ ] `docs/guides/flask-integration.md` — Flask/Connexion setup met alpha library componenten

---

### Fase 6 — Afwerking *(uitwerken)*

- [ ] ReadTheDocs project aanmaken op readthedocs.org
- [ ] GitHub webhook instellen (automatische builds bij push naar `main`)
- [ ] `README.md` badge updaten naar echte ReadTheDocs URL
- [ ] `mkdocs build --strict` valideren — geen broken links of warnings
- [ ] Controleer dat alle ~70 publieke exports in `__init__.py` gedocumenteerd zijn

---

## Tools & versies

| Package | Doel |
|---|---|
| `mkdocs-material` | MkDocs theme |
| `mkdocstrings[python]` | Auto-genereer API docs vanuit docstrings |
| `mkdocs-autorefs` | Automatische cross-references tussen pagina's |

**Lokaal draaien:**
```shell
# Installeer docs dependencies (uv pip vanwege mkdocs-material zonder Python 3.14 wheels)
uv pip install mkdocs-material "mkdocstrings[python]" mkdocs-autorefs

# Preview met live reload
mkdocs serve

# Build validatie
mkdocs build --strict
```

**ReadTheDocs:**
- Configuratie: `.readthedocs.yaml`
- Build OS: ubuntu-24.04, Python 3.11
- Alle optional extras worden geïnstalleerd voor volledige API reference rendering
