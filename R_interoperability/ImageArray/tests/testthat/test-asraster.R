library(magick)
skip_if_not_installed("ggplot2")
library(ggplot2)
library(EBImage)

# image file
img.file <- system.file("images", "sample.png", package = "EBImage")

test_that("levels", {
  # create image
  img <- magick::image_read(img.file)
  img <- magick::image_data(img)

  # create ImageArray
  imgarray <- createImageArray(img, n.levels = 2)

  # check as.raster
  imgarray2 <- as.raster(imgarray, max.pixel.size = 300)
  expect_true(all(dim(imgarray2) == dim(imgarray[[2]])[3:2]))
  imgarray2 <- as.raster(imgarray, level = 2)
  expect_true(all(dim(imgarray2) == dim(imgarray[[2]])[3:2]))
  expect_error(as.raster(imgarray, level = 3))
  expect_error(as.raster(imgarray, level = 1.2))
})
