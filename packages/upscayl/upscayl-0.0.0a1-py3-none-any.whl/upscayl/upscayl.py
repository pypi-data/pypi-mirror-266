import platform
import subprocess
from copy import copy
from dataclasses import dataclass
from os import path
from typing import IO, Callable, cast

from PIL import Image

UPSCAYL_EXE = path.join(
    path.dirname(__file__),
    "bin",
    platform.system(),
    "upscayl-bin" + ".exe" if platform.system() else "",
)


@dataclass
class UpscaylOption:
    scale: int
    tile_size: int
    model_path: str
    model_name: str
    gpu_id: str
    load_proc_save: str
    enable_tta: bool
    output_format: str
    enable_verbose_output: bool


def optToArgs(opt: UpscaylOption) -> list[str]:
    result = [
        "-s",
        f"{opt.scale}",
        "-t",
        f"{opt.tile_size}",
        "-m",
        f"{opt.model_path}",
        "-n",
        f"{opt.model_name}",
        "-g",
        f"{opt.gpu_id}",
        "-j",
        f"{opt.load_proc_save}",
        "-f",
        f"{opt.output_format}",
    ]

    if opt.enable_tta:
        result.append("-x")
    if opt.enable_verbose_output:
        result.append("-v")
    return result


@dataclass
class OverridePayload:
    option: UpscaylOption
    input: str
    output: str
    resample: Image.Resampling | None


@dataclass
class ProcessEvent:
    option: UpscaylOption
    input: str
    output: str
    resample: Image.Resampling | None
    isOverride: bool = False


def getModelScale(model: str) -> int:
    model_name = model.lower()
    initial_scale = 4
    if "x2" in model_name or "2x" in model_name:
        initial_scale = 2
    elif "x3" in model_name or "3x" in model_name:
        initial_scale = 3
    else:
        initial_scale = 4
    return initial_scale


def resizeImage(fileName: str, scale: float, resample: Image.Resampling | None):
    img = Image.open(fileName)
    resizeImg = img.resize(
        (int(img.width * scale), int(img.height * scale)),
        resample=resample,
    )
    img.close()
    resizeImg.save(fileName)
    resizeImg.close()


class Upscayl:
    OnProcess: list[Callable[[ProcessEvent], None]] = []
    Override: list[Callable[[OverridePayload], None]] = []
    Option: UpscaylOption
    _resample: Image.Resampling | None = None

    def __init__(
        self,
        model_name: str,
        scale: int = 4,
        tile_size: int = 0,
        model_path: str = "modules",
        gpu_id: str = "auto",
        load_proc_save: str = "1:2:2",
        enable_tta: bool = False,
        output_format: str = "png",
        enable_verbose_output: bool = False,
        resample: Image.Resampling | None = Image.Resampling.BILINEAR,
    ):
        """Init Upscayl

        Args:
            upscayl_exe (str, optional):_description_. upscayl execute.
            scale (int, optional): _description_. upscale ratio (can be 2, 3, 4. default=4).
            tile_size (int, optional): _description_. tile size (>=32/0=auto, default=0) can be 0,0,0 for multi-gpu.
            model_path (str, optional): _description_. folder path to the pre-trained models. default=models.
            model_name (str, optional): _description_. model name, default=realesr-animevideov3.
            gpu_id (str, optional): _description_. gpu device to use (default=auto) can be 0,1,2 for multi-gpu.
            load_proc_save (_type_, optional): _description_. thread count for load/proc/save (default=1:2:2) can be 1:2,2,2:2 for multi-gpu.
            enable_tta (bool, optional): _description_. enable tta mode.
            output_format (str, optional): _description_. output image format (jpg/png/webp, default=png).
            enable_verbose_output (bool, optional): _description_. verbose output.

        """
        self._resample = resample
        self.Option = UpscaylOption(
            scale=scale,
            tile_size=tile_size,
            model_path=model_path,
            model_name=model_name,
            gpu_id=gpu_id,
            load_proc_save=load_proc_save,
            enable_tta=enable_tta,
            output_format=output_format,
            enable_verbose_output=enable_verbose_output,
        )
        self.onProgress: Callable[[float], None] | None = None
        self.onDone: Callable[[str, str], None] | None = None

    def Process(self, input: str, output: str = ""):
        if path.isdir(input):
            raise Exception("input must be a file")
        if not path.exists(input):
            raise Exception(f"input {input} not found")
        opt = copy(self.Option)
        finallyScale = opt.scale
        modelScale = getModelScale(opt.model_name)
        if finallyScale > modelScale:
            raise Exception(
                f"model {opt.model_name} only support scale <= {modelScale}"
            )
        output_ = output
        resample = self._resample
        e = OverridePayload(opt, input, output_, resample)

        for func in self.Override:
            func(e)

        opt, output_, resample = e.option, e.output, e.resample
        opt.scale = modelScale

        if output_ == "":
            dot_index = input.rfind(".")
            output_ = (
                input[:dot_index]
                + f"_upscayl_{finallyScale}x_{opt.model_name}."
                + opt.output_format
            )

        for func in self.OnProcess:
            isOverride = (
                opt != self.Option or resample != self._resample or output_ != output
            )
            func(ProcessEvent(copy(opt), input, output_, resample, isOverride))

        self._process(input, output_, opt)
        if finallyScale != modelScale:
            resizeImage(output_, finallyScale / modelScale, resample)

    def _process(self, input: str, output: str, opt: UpscaylOption):
        process = subprocess.Popen(
            args=[UPSCAYL_EXE, "-i", input, "-o", output] + optToArgs(opt),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stderr: bytes = b""
        for line in cast(IO[bytes], process.stderr):
            stderr += line
            l = line.strip()

            if self.onProgress is not None:
                if l.endswith(b"%"):
                    self.onProgress(float(l[:-1]))
                    continue
                elif l == b"Upscayl Successful":
                    self.onProgress(100)
                    continue

            if self.onDone is not None:
                if l.endswith(b" done"):
                    input_, output_ = l[:-5].split(b" -> ")
                    self.onDone(input_.decode(), output_.decode())
        if process.wait() != 0:
            raise Exception(stderr.strip().decode())
