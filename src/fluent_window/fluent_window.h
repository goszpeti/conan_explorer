#ifndef FLUENT_WINDOW_H
#define FLUENT_WINDOW_H

#include <QWidget>
#include <QPropertyAnimation>

#include "ui_fluent_window.h"

#if defined(FLW_LIBRARY)
#define FLW_SHARED_EXPORT Q_DECL_EXPORT
#else
#define FLW_SHARED_EXPORT Q_DECL_IMPORT
#endif

#if defined(WIN32)
    #include <windows.h>
#endif

enum resizeDirection{
    defaulting, 
    top, left, right, bottom, 
    top_left, top_right, bottom_left, bottom_right
};


class FLW_SHARED_EXPORT FluentWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit FluentWindow(QMainWindow *parent = nullptr);
    ~FluentWindow();

public slots:
    void moveWindow(QEvent *event);

protected:
    bool eventFilter( QObject *dest, QEvent *event ) override;
    void setRestoreMaxButtonState();
    void enableNativeAnimations();
    void maximizeRestore();
    void mousePressEvent(QMouseEvent *event) override;
    bool nativeEvent(const QByteArray &eventType, void *message, long long * result) override;
    void handleResizeCursor(QHoverEvent *event , uint8_t x_offset=10, uint8_t y_offset=8);
    void resizeWindow(QMouseEvent *event);
    void toggle_left_menu();
private:

    std::unique_ptr<Ui::MainWindow> _ui{};
    std::unique_ptr<QPropertyAnimation> _left_anim{};

    QString _title_text{}; // save app title (hide for collapse)

    // window resize
    bool _resize_pressed = false;
    resizeDirection _resize_direction;
    QPoint _resize_point{};
    QRect _last_geometry{};

    // window move
    QPoint _drag_position{};
};


#endif // FLUENT_WINDOW_H
