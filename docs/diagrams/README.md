# Diagrams

The `.puml` files here are the sources; the `.png` and `.svg` next to each one are the rendered output, committed so the README works without a PlantUML renderer.

| Diagram | Source | What it shows |
|---|---|---|
| Component overview | [`architecture.puml`](architecture.puml) | Modules, what depends on what, where the model and dataset sit |
| Recognition sequence | [`recognition-sequence.puml`](recognition-sequence.puml) | One frame of the webcam loop, message by message |
| Training pipeline | [`training-pipeline.puml`](training-pipeline.puml) | Webcam footage to `models/model.p` |
| Screen flow | [`navigation.puml`](navigation.puml) | Login, sign-up, dashboard and the interpreter |

## Re-rendering

Any PlantUML install works:

```bash
plantuml -tpng architecture.puml          # PNG for GitHub
plantuml -tsvg architecture.puml          # SVG if you need it scalable
```

Without a local Java install, the [PlantUML web server](https://www.plantuml.com/plantuml) will render a `.puml` file pasted into it, and the [PlantUML extension for VS Code](https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml) previews them as you edit.

If you change a diagram, re-render both formats — the README embeds the PNGs, and the SVGs are there for anyone who wants a version that stays sharp when zoomed.
