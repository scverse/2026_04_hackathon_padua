library(magick)
library(EBImage)

# image file
img.file <- system.file("images", "sample.png", package = "EBImage")

test_that("read image", {
  # with magick-image
  img <- read_image(img.file, engine = "magick-image")
  expect_true(!is.null(img))
  expect_true(inherits(img, "magick-image"))

  # with EBImage
  img <- read_image(img.file, engine = "EBImage")
  expect_true(!is.null(img))
  expect_true(inherits(img, "Image"))
})
