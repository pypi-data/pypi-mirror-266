"""
Similar to ``xmovie``, make animations from xarray objects.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Hashable
    from typing import Any, Callable

    from matplotlib.figure import Figure
    from typing_extensions import Self
    from xarray import DataArray, Dataset


class Frames:

    def __init__(
        self,
        obj: DataArray | Dataset,
        func: Callable[[DataArray | Dataset], Figure | None],
        *,
        dim: Hashable,
        id_: str | None = None,
    ) -> None:
        """
        Parameters
        ----------
        obj
            Data to be plotted.
        func
            Function that takes a DataArray or Dataset and produces a matplotlib Figure
            and returns it (returning optional if not using Dask to write frames).
        dim
            Dimension along which frames are selected, before passing the data to `func`.
        id_
            Unique identifier for the movie frame file names
            (``xrframes_<id>_frame<zero-padded frame num>.png``).
        """
        self.obj = obj
        self.func = func
        self.dim = dim

        if id_ is None:
            import uuid

            id_ = str(uuid.uuid4()).split("-")[0]
        self.id_ = id_

        self._frame_pattern: str | None = None
        self.paths: list[Path] | None = None

    def preview(self, frame: int = 0) -> Self:
        """Preview a frame.

        This calls the plotting function for the selected frame
        and thus can be used before :meth:`write` has been called.

        Note that ``plt.show()`` is not applied.

        Parameters
        ----------
        frame
            Frame number to preview (plot).
        """
        if not 0 <= frame < self.obj.sizes[self.dim]:
            raise ValueError(f"frame number must be in [0, {self.obj.sizes[self.dim]})")
        self.func(self.obj.isel({self.dim: frame}))

        return self

    def write(
        self,
        path=None,
        *,
        parallel: bool | str = False,
        dpi: int = 200,
        transparent: bool = False,
        #
        parallel_kws: dict[str, Any] | None = None,
        plot_kws: dict[str, Any] | None = None,
        savefig_kws: dict[str, Any] | None = None,
    ) -> Self:
        """Write PNG frames.

        After writing, :attr:`paths` is set to the list of created PNGs.

        Parameters
        ----------
        path
            Directory to write the frames to.
            Default: temporary directory (``tempfile.gettempdir()``).
        parallel
            Save frames in parallel.

            - ``False``: sequential (default)
            - ``True`` or ``'Dask'``: parallel with Dask
            - ``'joblib'``: parallel with joblib
        dpi
            Used when saving the figures.
        """
        import matplotlib as mpl
        import matplotlib.pyplot as plt
        from rich.progress import MofNCompleteColumn, Progress, SpinnerColumn, TimeElapsedColumn

        if path is None:
            from tempfile import gettempdir

            path = Path(gettempdir())
        else:
            path = Path(path)

        if parallel_kws is None:
            parallel_kws = {}
        if plot_kws is None:
            plot_kws = {}
        if savefig_kws is None:
            savefig_kws = {}

        nd = len(str(self.obj.sizes[self.dim]))
        tpl = f"xrframes_{self.id_}_frame{{frame:0{nd}d}}.png"
        self._frame_pattern = (path / f"xrframes_{self.id_}_frame%0{nd}d.png").as_posix()

        savefig_kws_default = dict(
            dpi=dpi,
            bbox_inches="tight",
            pad_inches=0.05,
            transparent=transparent,
        )
        savefig_kws = {**savefig_kws_default, **savefig_kws}

        def write_frame(i: int) -> Path:
            with plt.ioff():
                fig = self.func(self.obj.isel({self.dim: i}), **plot_kws)
            if not isinstance(fig, plt.Figure):
                fig = plt.gcf()
            p = path / tpl.format(frame=i)
            fig.savefig(p, **savefig_kws)
            plt.close(fig)
            return p

        def write_frame_chunk(obj: DataArray | DataArray) -> DataArray:
            fig = self.func(obj.squeeze(), **plot_kws)
            if not isinstance(fig, plt.Figure):
                raise ValueError(
                    "for Dask, the supplied plotting function must return a matplotlib Figure"
                )
            p = obj["path"].item()
            fig.savefig(p, **savefig_kws)
            plt.close(fig)
            return obj["path"]

        if parallel is True or isinstance(parallel, str) and parallel.lower() == "dask":
            import xarray as xr

            from ._rich_dask import RichProgressDaskCallback

            current_backend = mpl.get_backend()
            mpl.use("agg")

            kws = dict()
            kws.update(parallel_kws)

            with RichProgressDaskCallback():
                chunked = self.obj.assign_coords(
                    {
                        "frame": (self.dim, range(self.obj.sizes[self.dim])),
                        "path": (
                            self.dim,
                            [path / tpl.format(frame=i) for i in range(self.obj.sizes[self.dim])],
                        ),
                    }
                ).chunk({self.dim: 1})
                ret = chunked.map_blocks(
                    write_frame_chunk,
                    template=xr.ones_like(chunked[self.dim]).chunk({self.dim: 1}),
                ).compute(**kws)
                frame_paths = ret.data.tolist()

            mpl.use(current_backend)
        elif isinstance(parallel, str) and parallel.lower() == "joblib":
            from joblib import delayed

            from ._rich_joblib import RichProgressJoblibParallel

            kws = dict(n_jobs=-2)
            kws.update(parallel_kws)

            frame_paths = RichProgressJoblibParallel(**kws)(
                delayed(write_frame)(i) for i in range(self.obj.sizes[self.dim])
            )
        elif parallel is False:
            with Progress(
                SpinnerColumn(finished_text="✔"),
                r" [progress.description]{task.description}",
                MofNCompleteColumn(),
                TimeElapsedColumn(),
            ) as progress:
                frame_paths = []
                for i in progress.track(
                    range(self.obj.sizes[self.dim]), description="Writing frame"
                ):
                    frame_paths.append(write_frame(i))
        else:
            raise ValueError(f"invalid value for `parallel`: {parallel!r}")

        self.paths = frame_paths

        return self

    # TODO: display (frame images viewer, with ipywidgets?)

    def to_mp4(
        self,
        out: str | Path = "./movie.mp4",
        *,
        fps: int = 10,
        crf: int = 17,
    ) -> None:
        """Make an MP4 movie from the PNG frames with FFmpeg.

        Parameters
        ----------
        fps
            Frame rate (per second).
        crf
            Constant rate factor (0--51, lower is better quality, 23 is FFmpeg's default).
            https://trac.ffmpeg.org/wiki/Encode/H.264#a1.ChooseaCRFvalue
        """
        import subprocess

        from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn

        if self._frame_pattern is None:
            raise RuntimeError("call `write_frames` first")

        out = Path(out).expanduser()

        # fmt: off
        cmd = [
            "ffmpeg",
            "-y",
            "-r", str(fps),
            "-i", self._frame_pattern,
            "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "veryslow",
            "-crf", str(crf),
            out.as_posix(),
        ]
        # fmt: on

        try:
            with Progress(
                SpinnerColumn(finished_text="✔"),
                r" [progress.description]{task.description}",
                TimeElapsedColumn(),
            ) as progress:
                task = progress.add_task("Making MP4", total=1)
                subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                )
                progress.advance(task, 1)
                progress.refresh()
        except subprocess.CalledProcessError as e:
            print(e.stderr.decode())
            raise

        return None

    def to_gif(
        self,
        out: str | Path = "./movie.gif",
        *,
        fps: int = 10,
        scale: str = "100%",
        magick: bool = True,
    ) -> None:
        """Make a GIF from the PNG frames with ImageMagick.

        Parameters
        ----------
        fps
            Frame rate (per second).
        scale
            Scaling applied when generating the output.
            For example
            ``'480x380'`` (maximum width and height in pixels, preserves original aspect ratio)
            or ``'50%'``.
        magick
            Use ``magick`` base command (new CLI for ImageMagick 7),
            i.e. ``magick convert`` instead of just ``convert``.
        """
        import subprocess

        from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn

        out = Path(out).expanduser()

        if not self.paths:
            raise RuntimeError("call `write_frames` first")

        files = [f.as_posix() for f in self.paths]

        # fmt: off
        cmd = [
            "convert",
            "-scale", scale,
            # "-unsharp", "0x6+0.5+0",
            "-dispose", "previous",
            "-delay", str(round(100 / fps)),
            "-loop", "0",
            "-layers", "optimizeframe",
            *files,
            out.as_posix(),
        ]
        # fmt: on

        if magick:
            cmd.insert(0, "magick")

        try:
            with Progress(
                SpinnerColumn(finished_text="✔"),
                r" [progress.description]{task.description}",
                TimeElapsedColumn(),
            ) as progress:
                task = progress.add_task("Making GIF", total=1)
                subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                )
                progress.advance(task, 1)
                progress.refresh()
        except subprocess.CalledProcessError as e:
            print(e.stderr.decode())
            raise

        return None

    def cleanup(self) -> Self:
        """Clean up (delete) the frame files associated with this instance.

        :attr:`paths` is reset to ``None``.
        """
        if self.paths is not None:
            for f in self.paths:
                f.unlink(missing_ok=True)
        self.paths = None
        self._frame_pattern = None

        return self
