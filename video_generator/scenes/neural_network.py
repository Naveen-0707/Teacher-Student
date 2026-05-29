"""
Neural-network scenes for YouTube Shorts (9:16 vertical layout).
Scenes: NeuralNetworkScene, NeuralTrainingScene
"""

import os
import random
import sys

from manim import *

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base_scene import ShortsScene   # noqa: E402

# ── palette ───────────────────────────────────────────────────────────────────
BG       = "#0a0a0f"
CYAN_C   = "#00f5ff"
PURPLE_C = "#9b00ff"
CONN_C   = "#1a3a5c"
MUTED_C  = "#888899"
WHITE_C  = "#ffffff"


# ─────────────────────────────────────────────────────────────────────────────
class NeuralNetworkScene(ShortsScene):
    """
    Vertical neural-network forward-pass animation.
    Layers stacked top-to-bottom to fill a 9:16 frame.
    """

    LAYER_SIZES  = [3, 5, 5, 3]
    LAYER_LABELS = ["Input", "Hidden", "Hidden", "Output"]
    NODE_R       = 0.22
    LAYER_GAP    = 1.9   # vertical gap between layers
    NODE_GAP     = 0.75  # horizontal gap between nodes in a layer

    def construct(self):
        self.camera.background_color = BG

        # Title block (top)
        title = Text("Neural Network", font_size=48, color=WHITE_C, weight=BOLD)
        subtitle = Text("How AI thinks", font_size=26, color=MUTED_C)
        title.to_edge(UP, buff=0.55)
        subtitle.next_to(title, DOWN, buff=0.18)

        # Build network (centred in the remaining vertical space)
        nodes, connections, labels = self._build_network()

        net = VGroup(connections, *[VGroup(*lyr) for lyr in nodes], labels)
        net.center().shift(DOWN * 0.4)   # slight downward push to clear title

        # ── Animate ──────────────────────────────────────────────────────────
        self.play(Write(title), FadeIn(subtitle), run_time=1.2)
        self.wait(0.2)

        self.play(Create(connections), run_time=1.4)

        for layer in nodes:
            self.play(*[GrowFromCenter(n) for n in layer], run_time=0.45)

        self.play(FadeIn(labels), run_time=0.6)
        self.wait(0.4)

        # Forward pass
        self._forward_pass(nodes)

        self.wait(1.5)

    # ── helpers ──────────────────────────────────────────────────────────────

    def _build_network(self):
        """Return (nodes_per_layer, connections VGroup, labels VGroup)."""
        total_height = (len(self.LAYER_SIZES) - 1) * self.LAYER_GAP

        nodes = []
        for i, size in enumerate(self.LAYER_SIZES):
            layer = []
            # Top layer at +total_height/2, bottom at -total_height/2
            y = total_height / 2 - i * self.LAYER_GAP
            for j in range(size):
                x = (j - (size - 1) / 2) * self.NODE_GAP

                glow = Circle(
                    radius=self.NODE_R + 0.1,
                    color=CYAN_C,
                    stroke_width=1,
                    stroke_opacity=0.2,
                    fill_opacity=0.06,
                )
                node = Circle(
                    radius=self.NODE_R,
                    color=CYAN_C,
                    fill_color=BG,
                    fill_opacity=1,
                    stroke_width=2,
                )
                glow.move_to([x, y, 0])
                node.move_to([x, y, 0])
                layer.append(VGroup(glow, node))
            nodes.append(layer)

        # Connections
        connections = VGroup()
        for i in range(len(nodes) - 1):
            for n1 in nodes[i]:
                for n2 in nodes[i + 1]:
                    ln = Line(
                        n1.get_center(), n2.get_center(),
                        stroke_width=0.7,
                        color=CONN_C,
                        stroke_opacity=0.55,
                    )
                    connections.add(ln)

        # Labels to the right of each layer
        labels = VGroup()
        for i, (size, name) in enumerate(zip(self.LAYER_SIZES, self.LAYER_LABELS)):
            y = total_height / 2 - i * self.LAYER_GAP
            max_x = ((size - 1) / 2) * self.NODE_GAP + self.NODE_R
            lbl = Text(name, font_size=18, color=MUTED_C)
            lbl.next_to([max_x, y, 0], RIGHT, buff=0.25)
            labels.add(lbl)

        return nodes, connections, labels

    def _forward_pass(self, nodes):
        info = Text("→ Forward Pass", font_size=26, color=CYAN_C)
        info.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(info))

        for i in range(len(nodes) - 1):
            # Light up source layer
            self.play(
                *[n[1].animate.set_fill(CYAN_C, opacity=0.6) for n in nodes[i]],
                run_time=0.25,
            )

            # Pulse dots travel to next layer
            dots = []
            for n1 in nodes[i]:
                for n2 in nodes[i + 1]:
                    d = Dot(n1.get_center(), radius=0.055, color=WHITE_C)
                    self.add(d)
                    dots.append(d.animate.move_to(n2.get_center()))

            self.play(*dots, run_time=0.45)

            # Light up dest layer
            self.play(
                *[n[1].animate.set_fill(PURPLE_C, opacity=0.7) for n in nodes[i + 1]],
                run_time=0.25,
            )

            # Dim source
            self.play(
                *[n[1].animate.set_fill(BG, opacity=1) for n in nodes[i]],
                run_time=0.2,
            )

        # Reset all
        self.play(
            *[n[1].animate.set_fill(BG, opacity=1) for lyr in nodes for n in lyr],
            run_time=0.3,
        )
        self.play(FadeOut(info))


# ─────────────────────────────────────────────────────────────────────────────
class NeuralTrainingScene(ShortsScene):
    """
    Shows a neural net beside a falling loss curve.
    Epoch counter ticks up; loss line drops while nodes pulse.
    """

    BG = BG

    def construct(self):
        self.camera.background_color = BG

        # ── Title ─────────────────────────────────────────────────────────────
        title = Text("AI Training", font_size=50, color=WHITE_C, weight=BOLD)
        subtitle = Text("Watching the model learn", font_size=24, color=MUTED_C)
        title.to_edge(UP, buff=0.5)
        subtitle.next_to(title, DOWN, buff=0.15)

        self.play(Write(title), FadeIn(subtitle), run_time=1.2)
        self.wait(0.3)

        # ── Small 3-layer net (upper-centre) ──────────────────────────────────
        net_nodes, net_conns = self._small_net()
        net_group = VGroup(net_conns, *[VGroup(*l) for l in net_nodes])
        net_group.move_to(UP * 1.8)

        self.play(Create(net_conns), run_time=0.8)
        for layer in net_nodes:
            self.play(*[GrowFromCenter(n) for n in layer], run_time=0.35)

        # ── Loss graph axes (lower half) ───────────────────────────────────────
        axes = Axes(
            x_range=[0, 10, 2],
            y_range=[0, 1.1, 0.25],
            x_length=5.5,
            y_length=3.0,
            axis_config={"color": MUTED_C, "stroke_width": 1.5},
            tips=False,
        )
        axes.move_to(DOWN * 2.5)

        x_label = Text("Epochs", font_size=18, color=MUTED_C)
        x_label.next_to(axes, DOWN, buff=0.2)
        y_label = Text("Loss", font_size=18, color=MUTED_C)
        y_label.next_to(axes, LEFT, buff=0.15)

        self.play(Create(axes), FadeIn(x_label), FadeIn(y_label), run_time=0.8)

        # ── Epoch counter ─────────────────────────────────────────────────────
        epoch_tracker = ValueTracker(0)
        epoch_label = always_redraw(
            lambda: Text(
                f"Epoch  {int(epoch_tracker.get_value()):>3}",
                font_size=24,
                color=CYAN_C,
            ).next_to(axes, UP, buff=0.25)
        )
        self.add(epoch_label)

        # Loss curve: exponential decay 1→0.07 over epochs 0-10
        def loss(t):
            return 0.93 * np.exp(-0.45 * t) + 0.07

        curve = axes.plot(loss, x_range=[0, 0], color=CYAN_C, stroke_width=2.5)
        self.add(curve)

        loss_dot = Dot(axes.c2p(0, loss(0)), radius=0.09, color="#ff0090")
        self.add(loss_dot)

        # Animate: draw curve + epoch counter + net pulsing
        def update_curve(mob, alpha):
            t = 10 * alpha
            mob.become(
                axes.plot(loss, x_range=[0, max(0.01, t)],
                          color=CYAN_C, stroke_width=2.5)
            )
            epoch_tracker.set_value(t)
            loss_dot.move_to(axes.c2p(t, loss(t)))

        self.play(
            UpdateFromAlphaFunc(curve, update_curve),
            *self._pulse_anims(net_nodes),
            run_time=6,
            rate_func=linear,
        )

        # ── Final result ──────────────────────────────────────────────────────
        done = Text("Training Complete ✓", font_size=28, color="#00ff41")
        done.next_to(axes, DOWN, buff=0.5)
        self.play(FadeIn(done, shift=UP * 0.2))
        self.wait(1.5)

    # ── helpers ──────────────────────────────────────────────────────────────

    def _small_net(self):
        sizes = [3, 4, 3]
        gap_x = 1.6
        gap_y = 0.65
        nodes = []
        for i, sz in enumerate(sizes):
            layer = []
            x = (i - 1) * gap_x
            for j in range(sz):
                y = (j - (sz - 1) / 2) * gap_y
                n = Circle(radius=0.18, color=CYAN_C,
                           fill_color=BG, fill_opacity=1, stroke_width=2)
                n.move_to([x, y, 0])
                layer.append(n)
            nodes.append(layer)

        conns = VGroup()
        for i in range(len(nodes) - 1):
            for a in nodes[i]:
                for b in nodes[i + 1]:
                    conns.add(Line(a.get_center(), b.get_center(),
                                   stroke_width=0.6, color=CONN_C,
                                   stroke_opacity=0.45))
        return nodes, conns

    def _pulse_anims(self, nodes):
        """Return a list of repeated flash animations for the training loop."""
        anims = []
        for layer in nodes:
            for n in layer:
                anims.append(
                    n.animate(rate_func=there_and_back).set_fill(PURPLE_C, opacity=0.75)
                )
        return anims
