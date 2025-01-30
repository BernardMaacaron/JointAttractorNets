# JointAttractorNets
**Dual implementations (Brian2 & PyTorch) of attractor networks for robotic joint-space representation.**

This repository explores attractor networks tailored to the joint-space of robots. It provides **two separate codebases**—one in **Brian2** and one in **PyTorch**—each maintained on its own branch, with a shared `docs` branch holding all documentation and references.

- **Brian2** Code: [Branch `Brian2-main`](https://github.com/BernardMaacaron/JointAttractorNets/tree/Brian2-main)  
- **PyTorch** Code: [Branch `PyTorch-main`](https://github.com/BernardMaacaron/JointAttractorNets/tree/PyTorch-main)

**Note:** The excel sheet contains the *architecture specifications* for the attractor networks can be found [here](https://istitutoitalianotecnologia-my.sharepoint.com/:x:/g/personal/bernard_maacaron_iit_it/EaOFdtbEMGZJgHFSxeu-YYEBvUkEcJdpQA-ryHbPz62cdQ?e=WyVAhq). Access is required.

---

## Branches

1. **docs** (Default Branch)  
   - Contains all **project documentation**, including usage guides, methodology, and references inside the [`docs/` folder](docs/).  
   - Development or updates to documentation should be done here.

2. **Brian2-main**  
   - Houses the **Brian2** implementation of the attractor networks.  
   - Pulls in updates from the `docs` branch (e.g., new or revised documentation).

3. **PyTorch-main**  
   - Houses the **PyTorch** implementation.  
   - Also merges or rebases documentation updates from the `docs` branch.

---

## Getting Started

1. **Clone the Repository**  
      ```bash
      git clone https://github.com/BernardMaacaron/JointAttractorNets.git
      cd JointAttractorNets
      ```
2. **Pick a Branch**
   - **Documentation** only: stay on `docs` (default).  
   - **Brian2** code:  
     ```bash
     git checkout Brian2-main
     ```
   - **PyTorch** code:  
     ```bash
     git checkout PyTorch-main
     ```
3. **Install Dependencies**  
   - Each code branch (Brian2 or PyTorch) may have its own `requirements.txt` or environment setup.  
   - See the `README.md` or instructions within that branch for more detail.

---

## Workflow Summary

1. **Documentation Updates**  
   - Always create or switch to a feature branch **from `docs`** (e.g., `git checkout docs` then `git checkout -b docs-updateFeature`).  
   - Make changes in `docs/`, then commit and push or open a PR into `docs`.  
   - Once approved, merge to keep `docs` updated.

2. **Code Development**  
   - Switch to the relevant code branch (`Brian2-main` or `PyTorch-main`).  
   - Create a feature branch for your work (e.g., `Brian2-featureXYZ` or `PyTorch-featureXYZ`).  
   - Implement, test, then commit and push. Open a PR back into the main code branch (`Brian2-main` or `PyTorch-main`).

3. **Syncing Documentation**  
   - If you need the latest docs in your code branch, **merge** or **rebase** from `docs`:
     ```bash
     # Example for Brian2
     git checkout Brian2-main
     git pull origin Brian2-main
     git merge docs  # or git rebase docs
     # Resolve any conflicts, commit, and push
     ```

4. **Release Workflow**  
   - When ready, tag or create releases separately in `Brian2-main` and `PyTorch-main` if you want distinct versioning.

---

## Repository Structure (High-Level)

While each branch will have its own structure, here’s a general layout you may encounter:

```
JointAttractorNets/
├─ docs/                     # Shared documentation (in the docs branch)
│   ├─ methodology.md
│   ├─ usage_guide.md
│   └─ ...
├─ Brian2-main/             # (exists on the Brian2-main branch)
│   ├─ requirements.txt
│   ├─ brian2_code/
│   └─ ...
└─ PyTorch-main/            # (exists on the PyTorch-main branch)
    ├─ requirements.txt
    ├─ pytorch_code/
    └─ ...
```

> **Note**: On GitHub, you’ll only see `docs/` in the **docs** branch. The `brian2_code/` or `pytorch_code/` structures live in their respective branches.

---

## Contributing

- **Documentation**: Open pull requests into the `docs` branch.  
- **Brian2 or PyTorch Code**: Open pull requests into the corresponding branch.  
- Follow any guidelines or style conventions outlined in our [Contributing Guide](docs/CONTRIBUTING.md) (if present).

---

## License

Include your chosen license details here, for example:

```
MIT License
```

[See LICENSE](LICENSE) for full terms.

---

### Questions or Feedback?

Feel free to [open an issue](https://github.com/BernardMaacaron/JointAttractorNets/issues) or submit a pull request. We welcome contributions, bug reports, and feature requests!
```
