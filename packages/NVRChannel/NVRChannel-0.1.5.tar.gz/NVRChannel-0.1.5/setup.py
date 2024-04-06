from setuptools import setup

setup(
    name='NVRChannel',
    version='0.1.5',
    author="Daniel Dunn",
    author_email="dannydunn@eternityforest.com",
    packages=['NVRChannel',"NVRChannel.NVRChannel", "NVRChannel.onvif"],
    package_data={'':["**/*.tflite", '**/*.txt', '**.*.json', "*.json","*.md",]},
    license='MIT',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/EternityForest/iot_devices",
    dependencies = [
    	"cv2",
    	"Pillow",
    	"tflite-runtime",
    	"icemedia",
        "scullery",
        "zeep"
    ]
)
