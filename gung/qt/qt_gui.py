try:
    from PySide.QtGui import (QAbstractPageSetupDialog,
                              QAbstractPrintDialog,
                              QAbstractProxyModel,
                              QAbstractTextDocumentLayout,
                              QAccessibleEvent,
                              QActionEvent,
                              QBitmap,
                              QBrush,
                              QCDEStyle,
                              QCleanlooksStyle,
                              QClipboard,
                              QClipboardEvent,
                              QCloseEvent,
                              QColor,
                              QConicalGradient,
                              QContextMenuEvent,
                              QCursor,
                              QDesktopServices,
                              QDoubleValidator,
                              QDrag,
                              QDragEnterEvent,
                              QDragLeaveEvent,
                              QDragMoveEvent,
                              QDropEvent,
                              QFileOpenEvent,
                              QFocusEvent,
                              QFont,
                              QFontDatabase,
                              QFontInfo,
                              QFontMetrics,
                              QFontMetricsF,
                              QGradient,
                              QHelpEvent,
                              QHideEvent,
                              QHoverEvent,
                              QIcon,
                              QIconDragEvent,
                              QIconEngine,
                              QIconEngineV2,
                              QImage,
                              QImageIOHandler,
                              QImageReader,
                              QImageWriter,
                              QInputContext,
                              QInputContextFactory,
                              QInputEvent,
                              QInputMethodEvent,
                              QIntValidator,
                              QItemSelection,
                              QItemSelectionModel,
                              QItemSelectionRange,
                              QKeyEvent,
                              QKeySequence,
                              QLinearGradient,
                              QMatrix,
                              QMatrix2x2,
                              QMatrix2x3,
                              QMatrix2x4,
                              QMatrix3x2,
                              QMatrix3x3,
                              QMatrix3x4,
                              QMatrix4x2,
                              QMatrix4x3,
                              QMatrix4x4,
                              QMotifStyle,
                              QMouseEvent,
                              QMoveEvent,
                              QMovie,
                              QPageSetupDialog,
                              QPaintDevice,
                              QPaintEngine,
                              QPaintEngineState,
                              QPaintEvent,
                              QPainter,
                              QPainterPath,
                              QPainterPathStroker,
                              QPalette,
                              QPen,
                              QPicture,
                              QPictureIO,
                              QPixmap,
                              QPixmapCache,
                              QPlastiqueStyle,
                              QPolygon,
                              QPolygonF,
                              QPrintDialog,
                              QPrintEngine,
                              QPrintPreviewDialog,
                              QPrintPreviewWidget,
                              QPrinter,
                              QPrinterInfo,
                              QProxyModel,
                              QPyTextObject,
                              QQuaternion,
                              QRadialGradient,
                              QRegExpValidator,
                              QRegion,
                              QResizeEvent,
                              QSessionManager,
                              QShortcutEvent,
                              QShowEvent,
                              QSortFilterProxyModel,
                              QSound,
                              QStandardItem,
                              QStandardItemModel,
                              QStatusTipEvent,
                              QStringListModel,
                              QStyleOptionDockWidgetV2,
                              QStyleOptionFrameV2,
                              QStyleOptionFrameV3,
                              QStyleOptionProgressBarV2,
                              QStyleOptionTabBarBaseV2,
                              QStyleOptionTabV2,
                              QStyleOptionTabV3,
                              QStyleOptionToolBoxV2,
                              QStyleOptionViewItemV2,
                              QStyleOptionViewItemV3,
                              QStyleOptionViewItemV4,
                              QSyntaxHighlighter,
                              QTabletEvent,
                              QTextBlock,
                              QTextBlockFormat,
                              QTextBlockGroup,
                              QTextBlockUserData,
                              QTextCharFormat,
                              QTextCursor,
                              QTextDocument,
                              QTextDocumentFragment,
                              QTextFormat,
                              QTextFragment,
                              QTextFrame,
                              QTextFrameFormat,
                              QTextImageFormat,
                              QTextInlineObject,
                              QTextItem,
                              QTextLayout,
                              QTextLength,
                              QTextLine,
                              QTextList,
                              QTextListFormat,
                              QTextObject,
                              QTextObjectInterface,
                              QTextOption,
                              QTextTable,
                              QTextTableCell,
                              QTextTableCellFormat,
                              QTextTableFormat,
                              QToolBarChangeEvent,
                              QTouchEvent,
                              QTransform,
                              QValidator,
                              QVector2D,
                              QVector3D,
                              QVector4D,
                              QWhatsThisClickedEvent,
                              QWheelEvent,
                              QWindowStateChangeEvent,
                              QWindowsStyle,
                              QWorkspace)
except ImportError:
    # noinspection PyUnresolvedReferences
    from PySide2.QtGui import (QAbstractPageSetupDialog,
                               QAbstractPrintDialog,
                               QAbstractProxyModel,
                               QAbstractTextDocumentLayout,
                               QAccessibleEvent,
                               QActionEvent,
                               QBitmap,
                               QBrush,
                               QCDEStyle,
                               QCleanlooksStyle,
                               QClipboard,
                               QClipboardEvent,
                               QCloseEvent,
                               QColor,
                               QConicalGradient,
                               QContextMenuEvent,
                               QCursor,
                               QDesktopServices,
                               QDoubleValidator,
                               QDrag,
                               QDragEnterEvent,
                               QDragLeaveEvent,
                               QDragMoveEvent,
                               QDropEvent,
                               QFileOpenEvent,
                               QFocusEvent,
                               QFont,
                               QFontDatabase,
                               QFontInfo,
                               QFontMetrics,
                               QFontMetricsF,
                               QGradient,
                               QHelpEvent,
                               QHideEvent,
                               QHoverEvent,
                               QIcon,
                               QIconDragEvent,
                               QIconEngine,
                               QIconEngineV2,
                               QImage,
                               QImageIOHandler,
                               QImageReader,
                               QImageWriter,
                               QInputContext,
                               QInputContextFactory,
                               QInputEvent,
                               QInputMethodEvent,
                               QIntValidator,
                               QItemSelection,
                               QItemSelectionModel,
                               QItemSelectionRange,
                               QKeyEvent,
                               QKeySequence,
                               QLinearGradient,
                               QMatrix,
                               QMatrix2x2,
                               QMatrix2x3,
                               QMatrix2x4,
                               QMatrix3x2,
                               QMatrix3x3,
                               QMatrix3x4,
                               QMatrix4x2,
                               QMatrix4x3,
                               QMatrix4x4,
                               QMotifStyle,
                               QMouseEvent,
                               QMoveEvent,
                               QMovie,
                               QPageSetupDialog,
                               QPaintDevice,
                               QPaintEngine,
                               QPaintEngineState,
                               QPaintEvent,
                               QPainter,
                               QPainterPath,
                               QPainterPathStroker,
                               QPalette,
                               QPen,
                               QPicture,
                               QPictureIO,
                               QPixmap,
                               QPixmapCache,
                               QPlastiqueStyle,
                               QPolygon,
                               QPolygonF,
                               QPrintDialog,
                               QPrintEngine,
                               QPrintPreviewDialog,
                               QPrintPreviewWidget,
                               QPrinter,
                               QPrinterInfo,
                               QProxyModel,
                               QPyTextObject,
                               QQuaternion,
                               QRadialGradient,
                               QRegExpValidator,
                               QRegion,
                               QResizeEvent,
                               QSessionManager,
                               QShortcutEvent,
                               QShowEvent,
                               QSortFilterProxyModel,
                               QSound,
                               QStandardItem,
                               QStandardItemModel,
                               QStatusTipEvent,
                               QStringListModel,
                               QStyleOptionDockWidgetV2,
                               QStyleOptionFrameV2,
                               QStyleOptionFrameV3,
                               QStyleOptionProgressBarV2,
                               QStyleOptionTabBarBaseV2,
                               QStyleOptionTabV2,
                               QStyleOptionTabV3,
                               QStyleOptionToolBoxV2,
                               QStyleOptionViewItemV2,
                               QStyleOptionViewItemV3,
                               QStyleOptionViewItemV4,
                               QSyntaxHighlighter,
                               QTabletEvent,
                               QTextBlock,
                               QTextBlockFormat,
                               QTextBlockGroup,
                               QTextBlockUserData,
                               QTextCharFormat,
                               QTextCursor,
                               QTextDocument,
                               QTextDocumentFragment,
                               QTextFormat,
                               QTextFragment,
                               QTextFrame,
                               QTextFrameFormat,
                               QTextImageFormat,
                               QTextInlineObject,
                               QTextItem,
                               QTextLayout,
                               QTextLength,
                               QTextLine,
                               QTextList,
                               QTextListFormat,
                               QTextObject,
                               QTextObjectInterface,
                               QTextOption,
                               QTextTable,
                               QTextTableCell,
                               QTextTableCellFormat,
                               QTextTableFormat,
                               QToolBarChangeEvent,
                               QTouchEvent,
                               QTransform,
                               QValidator,
                               QVector2D,
                               QVector3D,
                               QVector4D,
                               QWhatsThisClickedEvent,
                               QWheelEvent,
                               QWindowStateChangeEvent,
                               QWindowsStyle,
                               QWorkspace)
