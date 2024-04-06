from pathlib import Path, PurePath
from navconfig import config
from navconfig.logging import logger
from ...utils import fnExecutor
from .env import EnvSupport


class MaskInterface(EnvSupport):
    _variables: dict

    def __init__(self, **kwargs):
        self._masks: dict = {}
        self._variables = kwargs.pop("variables", {})
        self._environment = config
        super(MaskInterface, self).__init__(**kwargs)
        # filling Masks:
        masks = kwargs.pop("masks", None)
        if masks:
            self._masks = masks
            object.__setattr__(
                self,
                "masks",
                self._masks
            )
        self.process_masks()

    def mask_start(self, **kwargs):
        # Usable by Hooks
        self._masks: dict = kwargs.pop("masks", {})
        self._variables = kwargs.pop("variables", {})
        self._environment = config
        self.process_masks()

    def process_masks(self):
        for mask, replace in self._masks.items():
            # first: making replacement of masks based on vars:
            try:
                if mask in self._variables:
                    value = self._variables[mask]
                else:
                    value = replace.format(**self._variables)
            except Exception:
                value = replace
            try:
                value = fnExecutor(value, env=self._environment)
                self._masks[mask] = value
            except Exception as err:
                logger.warning(f"Mask Error: {err}")

    def mask_replacement(self, obj):
        for mask, replace in self._masks.items():
            if mask in self._variables:
                value = self._variables[mask]
            else:
                if str(obj) == mask and mask.startswith('#'):
                    # full replacement of the mask
                    obj = replace
                    return obj
                else:
                    # TODO: migrate to SafeDict
                    try:
                        value = str(obj).replace(mask, replace)
                    except (ValueError, TypeError):
                        value = str(obj).replace(mask, str(replace))
            if isinstance(obj, PurePath):
                obj = Path(value).resolve()
            else:
                obj = value
        return obj
