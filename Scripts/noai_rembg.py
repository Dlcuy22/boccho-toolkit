"""
This script provides a GUI for color-based background removal (Chroma Key).
It allows the user to select a color from a sample frame, adjust smoothing parameters,
and batch process all images in the input directory.

Functions:
- ChromaKeyApp: Main GUI class handling user interaction.
- process_image: Removes the specified color from a single image.
- process_batch: Iterates through the input directory and processes all images.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageFilter
import numpy as np
from pathlib import Path
import threading

# Configuration
INPUT_DIR = Path("input/raw_frames")
OUTPUT_DIR = Path("output/no_bg_frames")


class ChromaKeyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Key Background Removal")
        self.root.geometry("1000x650")

        self.target_color = np.array([0, 255, 0], dtype=np.uint8)  # Default Green
        self.tolerance = 50
        self.edge_smooth = 1.0
        self.erosion_size = 0

        self.current_image = None
        self.display_image = None
        self.image_path = None
        self.tk_image = None
        self.preview_mode = False

        self.setup_ui()
        self.load_first_image()

    def setup_ui(self):
        # Control Panel
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Instructions
        ttk.Label(
            control_frame, text="Instructions:", font=("Segoe UI", 10, "bold")
        ).pack(anchor=tk.W, pady=(0, 5))
        ttk.Label(control_frame, text="1. Pick background color.", wraplength=200).pack(
            anchor=tk.W
        )
        ttk.Label(
            control_frame, text="2. Adjust Tolerance, Smooth, Erosion.", wraplength=200
        ).pack(anchor=tk.W)
        ttk.Label(
            control_frame, text="3. Preview or Process All.", wraplength=200
        ).pack(anchor=tk.W)

        ttk.Separator(control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Color Display
        ttk.Label(control_frame, text="Selected Color:").pack(anchor=tk.W)
        self.color_swatch = tk.Label(
            control_frame, bg="#00FF00", width=20, height=2, relief=tk.SUNKEN
        )
        self.color_swatch.pack(pady=5)
        self.color_label = ttk.Label(control_frame, text="R:0 G:255 B:0")
        self.color_label.pack()

        ttk.Separator(control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Tolerance Slider
        self._create_slider(
            control_frame, "Tolerance:", 0, 150, self.update_tolerance, 50
        )

        # Edge Smoothing Slider
        self._create_slider(control_frame, "Edge Smooth:", 0, 10, self.update_smooth, 1)

        # Erosion Slider
        self._create_slider(
            control_frame, "Edge Erosion:", 0, 5, self.update_erosion, 0
        )

        ttk.Separator(control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Actions
        self.btn_preview = ttk.Button(
            control_frame, text="Toggle Preview", command=self.toggle_preview
        )
        self.btn_preview.pack(fill=tk.X, pady=5)

        self.btn_reset = ttk.Button(
            control_frame, text="Reset Image", command=self.reset_view
        )
        self.btn_reset.pack(fill=tk.X, pady=5)

        ttk.Separator(control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            control_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=5)

        self.btn_process = ttk.Button(
            control_frame,
            text="Process All Images",
            command=self.start_batch_processing,
        )
        self.btn_process.pack(fill=tk.X, pady=10)

        self.status_label = ttk.Label(control_frame, text="Ready")
        self.status_label.pack(side=tk.BOTTOM, pady=10)

        # Image Canvas
        self.canvas_frame = ttk.Frame(self.root)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="#333333")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.pick_color)

    def _create_slider(self, parent, label, min_val, max_val, callback, default):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        ttk.Label(frame, text=label).pack(anchor=tk.W)

        var = tk.DoubleVar(value=default)
        slider = ttk.Scale(
            frame,
            from_=min_val,
            to=max_val,
            orient=tk.HORIZONTAL,
            variable=var,
            command=lambda v: callback(v, val_label),
        )
        slider.pack(fill=tk.X)

        val_label = ttk.Label(frame, text=str(default))
        val_label.pack()
        return var

    def load_first_image(self):
        extensions = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
        if not INPUT_DIR.exists():
            messagebox.showerror("Error", f"Input directory not found: {INPUT_DIR}")
            return

        files = sorted(
            [
                f
                for f in INPUT_DIR.iterdir()
                if f.is_file() and f.suffix.lower() in extensions
            ]
        )

        if not files:
            messagebox.showwarning("Warning", f"No images found in {INPUT_DIR}")
            return

        self.image_path = files[0]
        self.load_image_to_canvas()

    def load_image_to_canvas(self):
        try:
            img = Image.open(self.image_path)
            display_size = (800, 600)
            img.thumbnail(display_size, Image.Resampling.LANCZOS)

            self.current_image = img.convert("RGBA")
            self.display_image = self.current_image.copy()

            self.update_canvas(self.display_image)
            self.status_label.config(text=f"Loaded: {self.image_path.name}")
            self.preview_mode = False

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

    def update_canvas(self, pil_image):
        self.tk_image = ImageTk.PhotoImage(pil_image)
        cw = self.canvas.winfo_width() or 800
        ch = self.canvas.winfo_height() or 600
        x = (cw - pil_image.width) // 2
        y = (ch - pil_image.height) // 2
        self.canvas.delete("all")
        self.canvas.create_image(
            max(x, 0), max(y, 0), anchor=tk.NW, image=self.tk_image
        )

    def pick_color(self, event):
        if self.preview_mode or self.current_image is None:
            return
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        img_w, img_h = self.current_image.size
        offset_x = (cw - img_w) // 2
        offset_y = (ch - img_h) // 2
        x = event.x - offset_x
        y = event.y - offset_y

        if 0 <= x < img_w and 0 <= y < img_h:
            r, g, b, _ = self.current_image.getpixel((x, y))
            self.target_color = np.array([r, g, b], dtype=np.uint8)
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            self.color_swatch.config(bg=hex_color)
            self.color_label.config(text=f"R:{r} G:{g} B:{b}")
            self.status_label.config(text="Color selected.")

    def update_tolerance(self, value, label):
        self.tolerance = int(float(value))
        label.config(text=str(self.tolerance))
        if self.preview_mode:
            self.refresh_preview()

    def update_smooth(self, value, label):
        self.edge_smooth = float(value)
        label.config(text=f"{self.edge_smooth:.1f}")
        if self.preview_mode:
            self.refresh_preview()

    def update_erosion(self, value, label):
        self.erosion_size = int(float(value))
        label.config(text=str(self.erosion_size))
        if self.preview_mode:
            self.refresh_preview()

    def refresh_preview(self):
        if self.current_image:
            preview_img = self.remove_background(self.current_image)
            self.update_canvas(preview_img)
            self.status_label.config(text="Preview updated")

    def remove_background(self, img_pil):
        # 1. Create a binary mask based on color difference
        img_array = np.array(img_pil)
        # Cast to float to avoid uint8 overflow
        rgb = img_array[:, :, :3].astype(np.float32)
        target = self.target_color.astype(np.float32)

        # Calculate Euclidean distance
        diff = np.sqrt(np.sum((rgb - target) ** 2, axis=2))

        # Create mask (True where pixel is foreground/NOT target color)
        # We want the foreground, so distance > tolerance
        mask_array = (diff > self.tolerance).astype(np.uint8) * 255

        # Convert mask to PIL Image for filtering
        mask_img = Image.fromarray(mask_array, mode="L")

        # 2. Apply Erosion (Shrink the mask to remove green halo)
        if self.erosion_size > 0:
            # MinFilter works as an erosion filter on light objects (white mask)
            mask_img = mask_img.filter(ImageFilter.MinFilter(self.erosion_size * 2 + 1))

        # 3. Apply Gaussian Blur (Soft Edges)
        if self.edge_smooth > 0:
            mask_img = mask_img.filter(
                ImageFilter.GaussianBlur(radius=self.edge_smooth)
            )

        # 4. Apply the modified mask to the original image's alpha channel
        if img_pil.mode != "RGBA":
            img_pil = img_pil.convert("RGBA")

        # Get processed PIL image
        result = img_pil.copy()
        result.putalpha(mask_img)

        return result

    def toggle_preview(self):
        if self.current_image is None:
            return
        if self.preview_mode:
            self.reset_view()
        else:
            self.status_label.config(text="Generating preview...")
            self.root.update()
            self.refresh_preview()
            self.preview_mode = True

    def reset_view(self):
        if self.current_image:
            self.update_canvas(self.current_image)
            self.preview_mode = False
            self.status_label.config(text="View reset")

    def start_batch_processing(self):
        if not INPUT_DIR.exists():
            messagebox.showerror("Error", "Input directory not found.")
            return
        if threading.active_count() > 1 and "BatchThread" in [
            t.name for t in threading.enumerate()
        ]:
            return

        self.btn_process.config(state=tk.DISABLED)
        self.status_label.config(text="Processing...")
        threading.Thread(
            target=self.process_batch, name="BatchThread", daemon=True
        ).start()

    def process_batch(self):
        extensions = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
        try:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            files = sorted(
                [
                    f
                    for f in INPUT_DIR.iterdir()
                    if f.is_file() and f.suffix.lower() in extensions
                ]
            )

            total = len(files)
            if total == 0:
                self.root.after(
                    0,
                    lambda: messagebox.showwarning("Warning", "No images to process."),
                )
                self.root.after(0, self.reset_ui_state)
                return

            for i, file_path in enumerate(files):
                try:
                    img = Image.open(file_path).convert("RGBA")
                    result = self.remove_background(img)
                    output_path = OUTPUT_DIR / f"{file_path.stem}.png"
                    result.save(output_path, "PNG")

                    progress = ((i + 1) / total) * 100
                    self.root.after(0, lambda p=progress: self.progress_var.set(p))
                    self.root.after(
                        0,
                        lambda t=f"Processing {i + 1}/{total}": (
                            self.status_label.config(text=t)
                        ),
                    )
                except Exception as e:
                    print(f"Error processing {file_path.name}: {e}")

            self.root.after(
                0, lambda: self.status_label.config(text="Batch processing complete!")
            )
            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Success", f"Processed {total} images.\nSaved to {OUTPUT_DIR}"
                ),
            )
        except Exception as e:
            self.root.after(
                0,
                lambda msg=str(e): messagebox.showerror(
                    "Error", f"Batch processing failed: {msg}"
                ),
            )
        finally:
            self.root.after(0, self.reset_ui_state)

    def reset_ui_state(self):
        self.btn_process.config(state=tk.NORMAL)
        self.progress_var.set(0)


def main():
    root = tk.Tk()
    ChromaKeyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
